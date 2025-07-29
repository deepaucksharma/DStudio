# System Design Frameworks

Structured approaches to tackle any system design problem systematically.

## Overview

These frameworks provide repeatable methodologies for approaching system design problems. They help ensure you cover all important aspects and communicate your design clearly.

## 📚 Core Frameworks

### RADIO Framework
**R**equirements → **A**rchitecture → **D**ata → **I**nterfaces → **O**perations

1. **Requirements**
   - Functional requirements
   - Non-functional requirements
   - Constraints and assumptions
   - Success metrics

2. **Architecture**
   - High-level design
   - Component breakdown
   - Communication patterns
   - Technology choices

3. **Data**
   - Data models
   - Storage systems
   - Consistency requirements
   - Access patterns

4. **Interfaces**
   - APIs (REST/GraphQL/gRPC)
   - Protocols
   - Data formats
   - Error handling

5. **Operations**
   - Deployment
   - Monitoring
   - Scaling
   - Failure handling

### 4S Method
**S**cenarios → **S**ervice → **S**torage → **S**cale

1. **Scenarios**
   - Use cases
   - User stories
   - Traffic patterns
   - Growth projections

2. **Service**
   - Service breakdown
   - Responsibilities
   - Dependencies
   - Interfaces

3. **Storage**
   - Data models
   - Database choice
   - Caching strategy
   - Backup/recovery

4. **Scale**
   - Bottleneck analysis
   - Horizontal scaling
   - Performance optimization
   - Cost optimization

### Problem-First Design
1. **Understand the Problem**
   - Core functionality
   - User needs
   - Business goals
   - Constraints

2. **Define Success**
   - Metrics
   - SLAs
   - Performance targets
   - User experience

3. **Design for the Common Case**
   - 80/20 rule
   - Simple first
   - Iterate complexity

4. **Handle Edge Cases**
   - Failure modes
   - Extreme scale
   - Security concerns

## 🎯 Specialized Frameworks

### For Real-Time Systems
**PULSE** Framework
- **P**rotocol selection
- **U**pdate mechanisms
- **L**atency requirements
- **S**tate synchronization
- **E**rror recovery

### For Data-Intensive Systems
**ACID-BASE** Analysis
- When to use ACID
- When to use BASE
- Hybrid approaches
- Migration strategies

### For Microservices
**MESH** Methodology
- **M**odule boundaries
- **E**vent communication
- **S**ervice discovery
- **H**ealth monitoring

## 📊 Decision Frameworks

### CAP Triangle Analysis
```
        Consistency
            /\
           /  \
          /    \
         /      \
    Availability  Partition Tolerance
```

For each component, explicitly choose 2 of 3.

### Trade-off Matrix
| Dimension | Option A | Option B | Recommendation |
|-----------|----------|----------|----------------|
| Performance | High | Medium | Depends on SLA |
| Cost | High | Low | Consider budget |
| Complexity | Low | High | Start simple |
| Reliability | Medium | High | Critical systems need B |

### Scaling Decision Tree
```
Traffic Increase?
├─ Yes → Predictable?
│   ├─ Yes → Scheduled scaling
│   └─ No → Auto-scaling
└─ No → Optimize current
```

## 💡 Communication Techniques

### Diagramming Best Practices
1. **Start Simple** - Boxes and arrows
2. **Layer Complexity** - Add detail gradually
3. **Use Standards** - Consistent symbols
4. **Label Everything** - Clear descriptions

### Explaining Trade-offs
- **Always give options** - Not just one solution
- **Quantify when possible** - Use numbers
- **Relate to requirements** - Tie back to goals
- **Consider evolution** - Future changes

### Handling Feedback
- **Listen actively** - Understand concerns
- **Adapt quickly** - Incorporate suggestions
- **Defend thoughtfully** - Explain reasoning
- **Admit unknowns** - It's okay not to know

## 🏃 Practice Exercises

### Framework Application
1. **Pick a framework** - Try RADIO first
2. **Choose a problem** - Start simple
3. **Time yourself** - 45 minutes
4. **Self-review** - What did you miss?

### Framework Comparison
Apply different frameworks to the same problem:
- URL Shortener with RADIO
- URL Shortener with 4S
- Compare outcomes

### Custom Framework
Create your own framework for:
- IoT systems
- Blockchain applications
- ML systems

## 📈 Interview Flow

### Opening (5 min)
- Clarify requirements
- Establish scope
- Confirm understanding

### Design (35 min)
- Apply framework
- Draw architecture
- Discuss trade-offs
- Deep dive on request

### Closing (5 min)
- Summarize design
- Discuss extensions
- Answer questions

---

*Start with the [RADIO Framework](radio-framework/) for a comprehensive approach, or explore [4S Method](4s-method/) for a simpler alternative.*