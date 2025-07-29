# The Universal System Design Interview Framework

## Overview

This framework synthesizes best practices from top tech companies to provide a systematic approach to any system design interview. Master this methodology, and you'll be prepared for interviews at Google, Amazon, Meta, Microsoft, or any company that values excellent system design.

!!! success "Framework Goals"
    - **Structured Approach**: Never miss critical components
    - **Time-Efficient**: Complete design within 45 minutes
    - **Comprehensive**: Cover all evaluation criteria
    - **Flexible**: Adapt to any system type

## The 8-Category Evaluation Framework

### 1. Problem Analysis & Requirements (25%)
**What Interviewers Assess**: Your ability to understand the problem and gather requirements systematically.

| Level | Indicators | Score |
|-------|------------|-------|
| **Outstanding** | Anticipates unstated requirements, connects to business goals | 4.0 |
| **Strong** | Systematic exploration, quantifies all constraints | 3.0-3.9 |
| **Adequate** | Covers basic requirements, some clarification | 2.0-2.9 |
| **Needs Work** | Jumps to solution, misses critical requirements | 1.0-1.9 |

### 2. System Architecture (20%)
**What Interviewers Assess**: Your ability to design scalable, maintainable systems.

| Level | Indicators | Score |
|-------|------------|-------|
| **Outstanding** | Novel insights, evolution path considered | 4.0 |
| **Strong** | Modern patterns, clear bounded contexts | 3.0-3.9 |
| **Adequate** | Standard architecture, basic separation | 2.0-2.9 |
| **Needs Work** | Monolithic thinking, unclear components | 1.0-1.9 |

### 3. Data Design (15%)
**What Interviewers Assess**: Your understanding of data modeling and storage systems.

| Level | Indicators | Score |
|-------|------------|-------|
| **Outstanding** | Complex consistency protocols, storage optimization | 4.0 |
| **Strong** | Polyglot persistence, caching strategies | 3.0-3.9 |
| **Adequate** | Basic schema design, appropriate DB choice | 2.0-2.9 |
| **Needs Work** | Single database for everything | 1.0-1.9 |

### 4. API Design (10%)
**What Interviewers Assess**: Your ability to design clean, usable interfaces.

| Level | Indicators | Score |
|-------|------------|-------|
| **Outstanding** | API gateway patterns, developer experience focus | 4.0 |
| **Strong** | Modern patterns (GraphQL/gRPC), comprehensive errors | 3.0-3.9 |
| **Adequate** | RESTful design, basic CRUD operations | 2.0-2.9 |
| **Needs Work** | No clear API definition | 1.0-1.9 |

### 5. Scalability Considerations (10%)
**What Interviewers Assess**: Your ability to design for growth.

| Level | Indicators | Score |
|-------|------------|-------|
| **Outstanding** | Novel scaling techniques, elasticity modeling | 4.0 |
| **Strong** | Multi-region design, auto-scaling policies | 3.0-3.9 |
| **Adequate** | Horizontal scaling, basic sharding | 2.0-2.9 |
| **Needs Work** | No scaling discussion | 1.0-1.9 |

### 6. Trade-off Analysis (10%)
**What Interviewers Assess**: Your decision-making and critical thinking.

| Level | Indicators | Score |
|-------|------------|-------|
| **Outstanding** | Creates decision matrices, strategic thinking | 4.0 |
| **Strong** | Quantified trade-offs, multiple alternatives | 3.0-3.9 |
| **Adequate** | Basic pros/cons, decisions justified | 2.0-2.9 |
| **Needs Work** | No trade-offs discussed | 1.0-1.9 |

### 7. Operational Excellence (5%)
**What Interviewers Assess**: Your understanding of production systems.

| Level | Indicators | Score |
|-------|------------|-------|
| **Outstanding** | Self-healing systems, predictive monitoring | 4.0 |
| **Strong** | Comprehensive observability, SLO/SLA defined | 3.0-3.9 |
| **Adequate** | Basic monitoring and alerting | 2.0-2.9 |
| **Needs Work** | No monitoring mentioned | 1.0-1.9 |

### 8. Communication Skills (5%)
**What Interviewers Assess**: Your ability to explain and collaborate.

| Level | Indicators | Score |
|-------|------------|-------|
| **Outstanding** | Teaches while designing, storytelling approach | 4.0 |
| **Strong** | Excellent visualizations, invites collaboration | 3.0-3.9 |
| **Adequate** | Clear explanations, basic diagrams | 2.0-2.9 |
| **Needs Work** | Unclear explanations, no visual aids | 1.0-1.9 |

## Step-by-Step Approach (45 Minutes)

### Phase 1: Requirements Gathering (0-8 minutes)

#### Step 1: Functional Requirements (3 minutes)
```
□ Core features (list 3-5 main functionalities)
□ User types and their needs
□ Out of scope features (clarify boundaries)
□ Success criteria
```

**Key Questions**:
- "What are the core features we need to support?"
- "Who are our users and what are their use cases?"
- "What features are explicitly out of scope?"
- "How do we measure success?"

#### Step 2: Non-Functional Requirements (2 minutes)
```
□ Scale (users, requests, data)
□ Performance (latency, throughput)
□ Availability and reliability targets
□ Consistency requirements
□ Security and compliance needs
```

**Key Questions**:
- "How many users are we designing for?"
- "What's our traffic pattern (steady/spiky)?"
- "What's our availability target?"
- "What are the latency requirements?"

#### Step 3: Capacity Estimation (3 minutes)
```
Quick Calculations:
- Users: _____ total, _____ daily active
- Requests: _____ QPS average, _____ QPS peak
- Storage: _____ TB total, _____ GB/day growth
- Bandwidth: _____ Gbps ingress, _____ Gbps egress
- Servers: _____ (based on capacity/server)
```

**Memory Helpers**:
- 1 day ≈ 100K seconds
- 1 billion users → 12K QPS (if each makes 1 request/day)
- Peak traffic ≈ 2-3x average
- 80/20 rule for cache hit rates

### Phase 2: High-Level Design (8-25 minutes)

#### Step 4: Architecture Overview (7 minutes)

**Draw Main Components**:
```
[Clients] → [LB] → [API Gateway] → [Services]
                           ↓
                    [Cache Layer]
                           ↓
                    [Data Stores]
                           ↓
                    [Message Queue] → [Workers]
```

**Essential Components Checklist**:
- [ ] Client applications (web, mobile, API)
- [ ] Load balancer / CDN
- [ ] API Gateway (rate limiting, auth)
- [ ] Application services
- [ ] Caching layer (multi-tier if needed)
- [ ] Primary data stores
- [ ] Message queues for async processing
- [ ] Background workers
- [ ] External service integrations

#### Step 5: Data Flow (5 minutes)

**Document Key Flows**:
1. **Read Path**: Client → CDN → LB → Service → Cache → DB
2. **Write Path**: Client → LB → Service → Queue → DB
3. **Async Processing**: Queue → Workers → External Services

#### Step 6: API & Data Model (5 minutes)

**Core APIs** (pick 3-5 most important):
```
POST /api/v1/resource
GET  /api/v1/resource/{id}
PUT  /api/v1/resource/{id}
GET  /api/v1/resource?filter=value&limit=20&offset=0
```

**Data Schema** (key entities only):
```sql
Users: id, email, created_at, metadata
Resources: id, user_id, data, created_at, updated_at
Events: id, resource_id, type, timestamp, payload
```

### Phase 3: Deep Dive (25-40 minutes)

#### Step 7: Component Details (10 minutes)

Pick 2-3 critical components and elaborate:

**For Each Component**:
- Internal architecture
- Technology choices with justification
- Scaling strategy
- Failure handling
- Performance optimizations

**Example Deep Dive - Caching Layer**:
```
L1 Cache: Application memory (microseconds)
L2 Cache: Redis cluster (milliseconds)
L3 Cache: CDN (tens of milliseconds)

Cache Strategy:
- Write-through for critical data
- Write-behind for analytics
- TTL based on data type
- Cache warming for predicted access
```

#### Step 8: Scale & Performance (5 minutes)

**Identify Bottlenecks**:
1. Database (solution: sharding, read replicas)
2. Application servers (solution: horizontal scaling, load balancing)
3. Network bandwidth (solution: CDN, compression)
4. Hot spots (solution: consistent hashing, smart routing)

**Scaling Strategies**:
```
Current: 1M users → Single region, master-slave DB
10M users → Multi-AZ, sharded DB, global CDN  
100M users → Multi-region, cell-based architecture
1B users → Edge computing, regional isolation
```

### Phase 4: Wrap-up (40-45 minutes)

#### Step 9: Trade-offs & Alternatives (3 minutes)

**The TRADE Method**:
- **T**arget: What are we optimizing for?
- **R**esources: What constraints do we have?
- **A**lternatives: What options exist?
- **D**ecision: What do we choose and why?
- **E**valuation: How do we measure success?

**Example Trade-off Presentation**:
```
"For data consistency, we have three options:
1. Strong consistency: Financial accuracy but higher latency
2. Eventual consistency: Better performance but temporary inconsistency  
3. Session consistency: Balance for user experience

Given our requirements, I recommend session consistency because..."
```

#### Step 10: Operational Considerations (2 minutes)

Quick coverage of:
- Monitoring & alerting strategy
- Deployment approach (blue-green, canary)
- Disaster recovery plan
- Security considerations
- Cost optimization opportunities

## Time Management for 45-Minute Interviews

### Visual Timeline
```
0  ├─────────────┤ 8  ├──────────────────────┤ 25 ├────────────────┤ 40 ├─────┤ 45
   Requirements        High-Level Design          Deep Dive          Wrap-up
   & Estimation        & Data Model               & Scaling
```

### Time Allocation by Problem Type

| Problem Type | Requirements | High-Level | Deep Dive | Trade-offs |
|-------------|--------------|------------|-----------|------------|
| **High-Traffic Service** | 5 min | 15 min | 20 min | 5 min |
| **Complex Business Logic** | 8 min | 12 min | 20 min | 5 min |
| **Data-Heavy System** | 5 min | 10 min | 25 min | 5 min |
| **Real-time System** | 7 min | 13 min | 20 min | 5 min |

### Warning Signs & Recovery

**You're Behind Schedule If**:
- 10 minutes in: Still gathering requirements
- 25 minutes in: No complete architecture
- 40 minutes in: Haven't discussed scaling

**Quick Recovery Actions**:
1. State: "Let me quickly outline the architecture"
2. Draw basic components in 2 minutes
3. Pick ONE component for deep dive
4. Mention scaling considerations briefly
5. Close with key trade-offs

## Common Pitfalls and How to Avoid Them

### 1. Not Thinking at Scale
❌ **Wrong**: "A single server with a database"
✅ **Right**: "Starting with a simple architecture that can evolve to handle millions of users"

**How to Avoid**: 
- Always clarify scale requirements first
- Design for 10x current requirements
- Show evolution path

### 2. Ignoring Failure Scenarios
❌ **Wrong**: Assuming everything works perfectly
✅ **Right**: "If the payment service fails, we queue the request and retry with exponential backoff"

**How to Avoid**:
- For each component, ask "How does this fail?"
- Include retry logic, circuit breakers, fallbacks
- Design for graceful degradation

### 3. Poor Time Management
❌ **Wrong**: Spending 20 minutes on requirements
✅ **Right**: Time-boxed phases with clear transitions

**How to Avoid**:
- Keep a timer visible
- Practice the timeline repeatedly
- Have transition phrases ready

### 4. Over-Engineering
❌ **Wrong**: "Let's use Kubernetes, Istio, and build our own database"
✅ **Right**: "We'll start simple with proven technologies and evolve as needed"

**How to Avoid**:
- Start with MVP design
- Show evolution path
- Justify complexity

### 5. Weak Communication
❌ **Wrong**: Silent thinking, messy diagrams
✅ **Right**: Think aloud, clear visuals, check understanding

**How to Avoid**:
- Narrate your thought process
- Use consistent diagram symbols
- Pause to ask "Does this make sense?"

## The TRADE Method for Trade-offs

When discussing any trade-off, use this structured approach:

### Example: Choosing a Database

**Target**: What are we optimizing for?
- "We need to optimize for high write throughput with eventual consistency"

**Resources**: What constraints do we have?
- "Budget allows for managed services, team has NoSQL experience"

**Alternatives**: What options exist?
```
Option A: DynamoDB
- Pros: Fully managed, auto-scaling, predictable performance
- Cons: Higher cost, vendor lock-in

Option B: Cassandra
- Pros: Open source, highly scalable, multi-datacenter
- Cons: Operational complexity, needs expertise

Option C: PostgreSQL with sharding
- Pros: ACID compliance, familiar technology
- Cons: Complex sharding logic, scaling limitations
```

**Decision**: What do we choose and why?
- "I recommend DynamoDB because operational simplicity outweighs the cost given our team size"

**Evaluation**: How do we measure success?
- "We'll monitor write latency, cost per transaction, and developer productivity"

## Practical Checklist

### Before the Interview
- [ ] Practice drawing standard architectures quickly
- [ ] Memorize capacity estimation shortcuts
- [ ] Prepare clarifying questions for different system types
- [ ] Review common technology trade-offs
- [ ] Practice time management with mock interviews

### During Requirements Phase
- [ ] Clarify functional requirements
- [ ] Quantify non-functional requirements
- [ ] Estimate capacity and scale
- [ ] Identify what's out of scope
- [ ] Confirm understanding before moving on

### During Design Phase
- [ ] Start with simple, complete architecture
- [ ] Show data flow clearly
- [ ] Define key APIs and data models
- [ ] Identify potential bottlenecks
- [ ] Discuss failure handling

### During Deep Dive
- [ ] Pick most critical components
- [ ] Explain technology choices
- [ ] Show detailed understanding
- [ ] Discuss scaling strategies
- [ ] Consider operational aspects

### During Wrap-up
- [ ] Summarize key decisions
- [ ] Acknowledge trade-offs
- [ ] Show evolution path
- [ ] Invite questions
- [ ] Express enthusiasm

## System-Specific Considerations

### For Real-time Systems
- WebSocket vs SSE vs Long polling
- Message ordering guarantees
- Connection management at scale
- Offline/online synchronization

### For Data-intensive Systems
- Batch vs stream processing
- Data pipeline architecture
- Schema evolution
- Data quality and validation

### For High-traffic Services
- Caching strategies (when, where, how)
- Load balancing algorithms
- Rate limiting approaches
- Geographic distribution

### For Transaction Systems
- ACID requirements
- Distributed transaction patterns
- Idempotency design
- Audit and compliance

## Final Success Tips

1. **Think Like a Senior Engineer**
   - Consider operational aspects
   - Think about team scalability
   - Focus on business value
   - Plan for evolution

2. **Communicate Effectively**
   - Use diagrams liberally
   - Think out loud
   - Check understanding frequently
   - Be open to feedback

3. **Show Depth and Breadth**
   - Complete system first (breadth)
   - Then dive deep strategically
   - Connect to real-world examples
   - Demonstrate experience

4. **Handle Pressure Gracefully**
   - Stay calm if you make mistakes
   - Adapt based on feedback
   - Show problem-solving process
   - Maintain positive attitude

Remember: The goal isn't to design a perfect system, but to demonstrate systematic thinking, technical knowledge, and communication skills. Focus on the process, and the outcome will follow.