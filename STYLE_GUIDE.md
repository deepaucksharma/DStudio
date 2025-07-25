# The Compendium Style Guide

## 🎯 Voice & Tone

### Our Voice Is:
- **Authoritative but approachable** - Expert knowledge without arrogance
- **Dense but digestible** - Every word matters, but readable
- **Practical but principled** - Theory grounded in reality
- **Visual but precise** - Diagrams with exact meanings

### Our Voice Is NOT:
- ❌ Verbose or academic
- ❌ Condescending or overly simplistic  
- ❌ Tool-specific or vendor-biased
- ❌ Theoretical without application

## 📝 Writing Principles

### 1. Density Over Length
```markdown
❌ BAD: "Distributed systems are complex software architectures that span multiple machines, 
and they require careful consideration of various factors including network latency, 
failure modes, and consistency models."

✅ GOOD: "Distributed systems = complexity across machines. Key challenges: latency, 
failures, consistency."
```

### 2. Tables Over Text
```markdown
❌ BAD: "Redis provides fast access times but limited query capabilities, while 
PostgreSQL offers rich queries but slower performance..."

✅ GOOD:
| Database | Speed | Queries | Use When |
|----------|-------|---------|----------|
| Redis | Microseconds | Key-only | Cache, counters |
| PostgreSQL | Milliseconds | Full SQL | Complex data |
```

### 3. Diagrams Over Descriptions
```markdown
❌ BAD: "The client sends a request to the load balancer, which forwards it to one 
of three servers..."

✅ GOOD:
\`\`\`mermaid
graph LR
    Client --> LB[Load Balancer]
    LB --> S1[Server 1]
    LB --> S2[Server 2]
    LB --> S3[Server 3]
\`\`\`
```

## 🎨 Visual Components

### Component Boxes Usage

#### axiom-box (Purple)
For fundamental laws and principles:
```markdown
<div class="axiom-box">
<h3>⚡ Law 1: Correlated Failure</h3>
<p>Things fail together, not independently.</p>
</div>
```

#### decision-box (Green)
For choices and trade-offs:
```markdown
<div class="decision-box">
<h3>🎯 When to Use Caching</h3>
<ul>
<li>Read-heavy workload (>90% reads)</li>
<li>Expensive computations</li>
<li>Tolerable staleness</li>
</ul>
</div>
```

#### failure-vignette (Red)
For disaster stories:
```markdown
<div class="failure-vignette">
<h3>🔥 The Day We Lost 3 Data Centers</h3>
<p>Hurricane Sandy taught us about correlated failures...</p>
</div>
```

#### truth-box (Blue)
For key insights:
```markdown
<div class="truth-box">
<h3>💡 The Real Cost of Microservices</h3>
<p>Every service boundary is a failure boundary.</p>
</div>
```

## 📊 Standard Formats

### Pattern Structure
1. **Quick Reference Box** - Problem, solution, trade-offs
2. **The Problem** - Why this exists (2-3 paragraphs)
3. **The Solution** - Core concept with diagram
4. **Implementation** - Code or pseudocode
5. **Trade-offs Table** - Always include
6. **Real Examples** - 2+ production cases
7. **Related Patterns** - Cross-references

### Case Study Structure
1. **Challenge Box** - Scale, constraints, goals
2. **Requirements** - Functional and non-functional
3. **High-Level Design** - Architecture diagram
4. **Deep Dive** - Interesting technical challenge
5. **Lessons Learned** - 3-5 key insights

### Trade-off Tables
Always include these three dimensions:
```markdown
| Aspect | Benefit | Cost |
|--------|---------|------|
| Performance | [speed gain] | [resource cost] |
| Complexity | [simplicity] | [limitations] |  
| Reliability | [failure handling] | [overhead] |
```

## 🔤 Terminology Standards

### Consistent Terms
- **Laws** not Axioms (for the 7 fundamentals)
- **Pillars** not Principles (for the 5 categories)
- **QPS** not RPS (queries per second)
- **p99** not 99th percentile
- **Nodes** not servers/machines (unless specific)

### Capitalization
- Law names: "Law 1: Correlated Failure" (title case)
- Pattern names: "Circuit Breaker pattern" (only first word)
- Technologies: "PostgreSQL" not "Postgres"
- Acronyms: "CAP theorem" not "CAP Theorem"

## 🔗 Linking Conventions

### Internal Links
```markdown
✅ GOOD: [Law 1: Correlated Failure](/part1-axioms/law1-failure/)
❌ BAD: [Click here](../law1-failure/index.md)
```

### Cross-References Format
```markdown
**Related**: [Circuit Breaker](/patterns/circuit-breaker) • 
[Bulkhead](/patterns/bulkhead) • [Timeout](/patterns/timeout)
```

### Reference Citations
```markdown
¹ [Lamport, L. (1998). The Part-Time Parliament](https://lamport.azurewebsites.net/pubs/lamport-paxos.pdf)
```

## 📐 Code Standards

### Code Block Format
```python
# Always include language hint
def circuit_breaker(failure_threshold=5, timeout=60):
    """
    One-line purpose.
    
    Details if needed.
    """
    # Implementation focused on concept, not production-ready
    pass
```

### Pseudocode When Appropriate
```
ALGORITHM: Consistent Hashing
1. Hash each node to ring position
2. Hash key to ring position  
3. Walk clockwise to first node
4. That node owns the key
```

## 🎯 Content Priorities

### Must Have
- ✅ Visual diagram or table
- ✅ Real-world example
- ✅ Trade-offs explicitly stated
- ✅ Cross-references to laws/pillars

### Should Have
- 📊 Performance numbers
- 🔥 Failure story
- 💡 Counter-intuitive insight
- 🛠️ Implementation snippet

### Nice to Have
- 📚 Academic references
- 🏢 Company case studies
- 📈 Benchmarks
- 🎓 Exercises

## ❌ What to Avoid

### Writing Anti-patterns
1. **No fluff phrases**: "It's important to note that...", "As we all know..."
2. **No hedging**: "might", "could", "possibly" - be definitive
3. **No vendor pitches**: Technology-agnostic always
4. **No untested code**: Every example must work
5. **No walls of text**: Break with headers, lists, tables

### Common Mistakes
- 🚫 Creating new "axiom" references (use law1-law7)
- 🚫 Relative path links (use absolute from /docs)
- 🚫 Missing trade-offs section
- 🚫 Abstract without concrete
- 🚫 Tool-specific solutions

## ✍️ Writing Checklist

Before submitting content:
- [ ] Would I pay to read this?
- [ ] Can I remove 30% more words?
- [ ] Is there a visual element?
- [ ] Are trade-offs explicit?
- [ ] Did I test all code?
- [ ] Are links absolute paths?
- [ ] Does it reference laws/pillars?
- [ ] Is there a real example?

## 📚 Style Examples

### Good Opening
```markdown
# Circuit Breaker Pattern

<div class="axiom-box">
<h3>⚡ Quick Reference</h3>
<ul>
<li><strong>Problem:</strong> Cascading failures from unhealthy dependencies</li>
<li><strong>Solution:</strong> Fail fast when error rate exceeds threshold</li>
<li><strong>Trade-off:</strong> Availability over correctness</li>
<li><strong>Use when:</strong> Calling external services</li>
</ul>
</div>
```

### Good Trade-off Table
```markdown
| State | Success Rate | Behavior | Recovery |
|-------|--------------|----------|----------|
| Closed | > 95% | Normal operation | N/A |
| Open | < 50% | Fail immediately | Wait timeout |
| Half-Open | Testing | Limited requests | Monitor health |
```

### Good Cross-Reference
```markdown
The Circuit Breaker pattern directly addresses [Law 1: Correlated Failure](/part1-axioms/law1-failure/) by preventing cascade failures. It works well with [Bulkhead](/patterns/bulkhead) for isolation and [Timeout](/patterns/timeout) for bounded operations.
```

---

*Remember: Every sentence should teach something. If it doesn't, delete it.*