# Common Mistakes in Google System Design Interviews

## Overview

This guide covers the most common mistakes candidates make in Google system design interviews and how to avoid them. Learning from these pitfalls can significantly improve your interview performance.

## Top 10 Critical Mistakes

### 1. Not Thinking at Google Scale

**Mistake**: Designing for thousands of users instead of billions
```
❌ Wrong: "We'll use a single PostgreSQL database"
✅ Right: "We'll shard across thousands of database instances"
```

**How to Avoid**:
- Always clarify scale requirements upfront
- Think in terms of billions of users from the start
- Consider global distribution
- Plan for 100x growth

### 2. Over-Engineering Too Early

**Mistake**: Starting with microservices, Kubernetes, and service mesh
```
❌ Wrong: "Let's use 50 microservices with Istio service mesh"
✅ Right: "Let's start with a monolith and split as we scale"
```

**How to Avoid**:
- Start simple, evolve the design
- Add complexity only when justified
- Explain the evolution path
- MVP first, then optimize

### 3. Ignoring Failure Scenarios

**Mistake**: Assuming everything works perfectly
```
❌ Wrong: "The service calls the database and returns the result"
✅ Right: "The service calls the database with timeout, retry logic, and circuit breaker"
```

**How to Avoid**:
- Consider failure at every component
- Discuss fallback strategies
- Plan for graceful degradation
- Include monitoring and alerting

### 4. Poor Time Management

**Mistake**: Spending 30 minutes on requirements gathering
```
Time allocation:
❌ Wrong: Requirements (30min) → Design (10min) → Discussion (5min)
✅ Right: Requirements (5-10min) → Design (25-30min) → Deep dive (10min)
```

**How to Avoid**:
- Set a timer for each phase
- Move forward even with some ambiguity
- Leave time for deep dives
- Practice time management

### 5. Missing the Big Picture

**Mistake**: Getting lost in implementation details
```
❌ Wrong: Spending 15 minutes on database index optimization
✅ Right: Cover end-to-end flow first, then dive into specifics
```

**How to Avoid**:
- Start with high-level architecture
- Complete the full system before optimizing
- Use the "breadth-first" approach
- Save details for deep dive

### 6. Neglecting Data Consistency

**Mistake**: Hand-waving consistency requirements
```
❌ Wrong: "We'll just use eventual consistency everywhere"
✅ Right: "Payment requires strong consistency, while view counts can be eventually consistent"
```

**How to Avoid**:
- Identify consistency requirements per feature
- Explain trade-offs clearly
- Know when to use different consistency models
- Consider business impact

### 7. Forgetting About Costs

**Mistake**: Proposing expensive solutions without justification
```
❌ Wrong: "Store everything in memory for fast access"
✅ Right: "Use tiered storage: hot data in memory, warm in SSD, cold in HDD"
```

**How to Avoid**:
- Consider cost at Google scale
- Propose cost-effective solutions
- Discuss storage tiers
- Mention optimization strategies

### 8. Not Asking Clarifying Questions

**Mistake**: Making assumptions without confirmation
```
❌ Wrong: Assuming requirements silently
✅ Right: "Should the system support video uploads? What's the maximum file size?"
```

**Good Questions to Ask**:
- Functional requirements?
- Scale requirements?
- Performance requirements?
- Consistency requirements?
- Cost constraints?

### 9. Weak API Design

**Mistake**: Vague or incomplete API definitions
```
❌ Wrong: "The API returns search results"
✅ Right: 
    GET /search?q=term&limit=20&offset=0
    Response: {
      results: [...],
      total: 1000,
      next_page_token: "..."
    }
```

**How to Avoid**:
- Define clear endpoints
- Include request/response formats
- Consider pagination
- Plan for versioning

### 10. Insufficient Monitoring Discussion

**Mistake**: Adding monitoring as an afterthought
```
❌ Wrong: "We'll add some monitoring"
✅ Right: "We'll monitor QPS, latency (p50/p95/p99), error rates, and set up alerts for SLA violations"
```

**Key Metrics to Discuss**:
- Latency percentiles
- Throughput metrics
- Error rates
- Business metrics
- SLA monitoring

## Behavioral Mistakes

### Not Thinking Out Loud
- Explain your reasoning
- Share trade-off considerations
- Verbalize your thought process

### Being Defensive
- Accept feedback gracefully
- Iterate on your design
- Show flexibility

### Not Managing Ambiguity
- Make reasonable assumptions
- State them clearly
- Move forward with confidence

## Technical Knowledge Gaps

### Common Gaps to Address

1. **Distributed Systems Fundamentals**
   - CAP theorem
   - Consensus protocols
   - Consistency models

2. **Google Technologies**
   - Bigtable vs Spanner
   - MapReduce basics
   - GFS/Colossus concepts

3. **Scaling Patterns**
   - Sharding strategies
   - Caching layers
   - Load balancing

4. **System Design Patterns**
   - Event sourcing
   - CQRS
   - Saga pattern

## Communication Mistakes

### Poor Diagramming
```
❌ Wrong: Messy, unlabeled boxes
✅ Right: Clear components with data flow arrows
```

### Using Jargon Incorrectly
- Understand terms before using them
- Explain acronyms
- Be precise with technical terms

### Not Engaging the Interviewer
- Ask for feedback
- Check understanding
- Invite questions

## Design Mistakes by System Type

### For Search Systems
- Forgetting about ranking
- Ignoring index updates
- Missing query understanding

### For Storage Systems
- No deduplication strategy
- Ignoring durability requirements
- Missing consistency model

### For Real-time Systems
- Not considering WebSockets
- Ignoring connection management
- Missing message ordering

### For Video Systems
- Forgetting CDN design
- Missing adaptive bitrate
- Ignoring storage costs

## How to Practice Avoiding These Mistakes

### Mock Interview Checklist
- [ ] Clarified all requirements
- [ ] Designed for Google scale
- [ ] Addressed failure scenarios
- [ ] Managed time well
- [ ] Covered full system
- [ ] Discussed monitoring
- [ ] Considered costs
- [ ] Drew clear diagrams

### Self-Review Questions
1. Did I think big enough?
2. Is my design simple to start?
3. How does each component fail?
4. What are the bottlenecks?
5. How much would this cost?

## Recovery Strategies

### When You Realize a Mistake
1. **Acknowledge it**: "I realize I should consider..."
2. **Adjust quickly**: Make the correction
3. **Learn from it**: Don't repeat in the interview
4. **Move forward**: Don't dwell on it

### When Stuck
1. **State the challenge**: "I'm considering how to..."
2. **Think out loud**: Share your options
3. **Make a decision**: Choose and explain
4. **Mark for revisit**: "We can optimize this later"

## Final Tips

1. **Practice System Design Daily**: Even 30 minutes helps
2. **Review Real Systems**: Study how Google actually built things
3. **Get Feedback**: Mock interviews are invaluable
4. **Learn from Rejections**: Each interview teaches something

Remember: Google values clear thinking, scalable designs, and good communication over perfect solutions. Focus on demonstrating these qualities while avoiding common pitfalls.

[Return to Google Interview Guide](./index.md)