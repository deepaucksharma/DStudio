# Exercise Template Usage Guide

This guide helps educators and contributors create consistent, high-quality exercises across all content types in the Compendium.

## Overview

We have four main exercise templates:
1. **Axiom Exercises** - Understanding fundamental constraints
2. **Pillar Exercises** - Building complex systems
3. **Pattern Exercises** - Implementing specific solutions
4. **Quantitative Exercises** - Mathematical analysis and modeling

## Choosing the Right Template

| Content Type | Template | Focus | Typical Duration |
|--------------|----------|-------|------------------|
| Axioms | `EXERCISE_TEMPLATE_AXIOM.md` | Experience & measurement | 30 min - 2 hours |
| Pillars | `EXERCISE_TEMPLATE_PILLAR.md` | Design & architecture | 1 - 8 hours |
| Patterns | `EXERCISE_TEMPLATE_PATTERN.md` | Implementation & debugging | 45 min - 4 hours |
| Quantitative | `EXERCISE_TEMPLATE_QUANTITATIVE.md` | Calculation & analysis | 30 min - 3 hours |

## General Principles

### 1. Learning Objectives First
Before creating exercises, clearly define:
- What students should be able to DO after completing exercises
- How they'll demonstrate mastery
- What misconceptions to address

### 2. Progressive Difficulty
Structure exercises in increasing complexity:
```
⭐ (Beginner) → ⭐⭐⭐ (Intermediate) → ⭐⭐⭐⭐⭐ (Expert)
```

### 3. Real-World Context
- Use actual company examples (with citations)
- Include real production metrics
- Reference published architectures
- Connect to actual engineering decisions

### 4. Multiple Learning Styles
Each exercise set should include:
- **Hands-on labs** (kinesthetic learners)
- **Visual diagrams** (visual learners)
- **Thought experiments** (reflective learners)
- **Team exercises** (collaborative learners)

## Template Customization

### For Axiom Exercises

Focus on **experiencing** the axiom:
```markdown
### Lab 1: Measure [Axiom] Yourself
- Use tools like ping, traceroute, load generators
- Collect real measurements
- Feel the constraint personally

### Lab 2: Break the [Axiom]
- Intentionally violate the axiom
- Observe failure modes
- Learn why the axiom matters
```

Example for Latency Axiom:
- Measure speed of light delays
- Try to beat fundamental limits
- Calculate minimum possible latencies

### For Pillar Exercises

Focus on **system design**:
```markdown
### Exercise 1: Design [System Type]
Given:
- Scale: 1M users, 100K requests/sec
- Budget: $50K/month
- Team: 5 engineers
- SLA: 99.99% uptime

Design complete architecture addressing [Pillar]
```

Example for State Pillar:
- Design globally distributed database
- Handle consistency requirements
- Make trade-off decisions with justification

### For Pattern Exercises

Focus on **implementation**:
```markdown
### Workshop 1: Implement [Pattern]
Starting code provided:
- Basic structure
- Test suite
- Infrastructure (Docker)

Your task:
1. Complete implementation
2. Pass all tests
3. Handle edge cases
```

Example for Circuit Breaker:
- Implement state machine
- Add failure detection
- Test under load

### For Quantitative Exercises

Focus on **calculation and analysis**:
```markdown
### Problem 1: Calculate [Metric]
Given production data:
- Arrival rate: λ = 1000 req/s
- Service time: μ = 10ms
- Servers: c = 50

Calculate:
a) Utilization
b) Queue length
c) Wait time
```

## Quality Standards

### Every Exercise Must Have

1. **Clear Success Criteria**
   ```markdown
   ✅ All tests pass
   ✅ Performance targets met
   ✅ Documentation complete
   ```

2. **Time Estimates**
   ```markdown
   **Time**: 45 minutes
   **Format**: Individual or Pair
   ```

3. **Difficulty Rating**
   ```markdown
   **Difficulty**: ⭐⭐⭐ (Intermediate)
   ```

4. **Prerequisites**
   ```markdown
   **Prerequisites**: 
   - Basic Python knowledge
   - Understanding of [Concept X]
   - Docker installed
   ```

### Solutions and Hints

Always provide:
1. **Hints** (progressive disclosure)
   ```markdown
   <details>
   <summary>Hint 1</summary>
   Consider what happens when...
   </details>
   ```

2. **Complete Solutions**
   ```markdown
   <details>
   <summary>Reference Solution</summary>
   
   ```python
   # Full implementation with comments
   ```
   
   **Key Insights**:
   - Why this approach works
   - Trade-offs made
   - Alternative solutions
   </details>
   ```

## Common Pitfalls to Avoid

### 1. Vague Requirements
❌ "Build a distributed system"
✅ "Build a key-value store handling 10K ops/sec with 99.9% availability"

### 2. Missing Context
❌ "Implement pattern X"
✅ "Netflix uses pattern X for Y. Implement it for similar use case Z"

### 3. No Validation
❌ Manual checking only
✅ Automated test suite provided

### 4. Unrealistic Scenarios
❌ Toy examples with no real application
✅ Simplified versions of actual production systems

## Exercise Progression

### Within a Topic
1. **Understand** - Basic concepts and measurements
2. **Apply** - Use in controlled scenarios
3. **Analyze** - Evaluate trade-offs
4. **Create** - Design new solutions
5. **Evaluate** - Judge others' solutions

### Across Topics
Create exercises that connect concepts:
- Axiom + Pillar: "How does latency affect state management?"
- Pillar + Pattern: "Which patterns best implement this pillar?"
- Pattern + Quantitative: "Calculate the performance of this pattern"

## Infrastructure and Tools

### Provide Everything Needed
```yaml
# docker-compose.yml for exercises
version: '3.8'
services:
  app:
    build: .
    environment:
      - EXERCISE_MODE=true
  
  redis:
    image: redis:7-alpine
    
  postgres:
    image: postgres:15
    
  monitoring:
    image: prom/prometheus
```

### Include Helper Scripts
```bash
# run_exercise.sh
#!/bin/bash
echo "Setting up exercise environment..."
docker-compose up -d
echo "Running tests..."
pytest tests/
echo "Checking performance..."
./load_test.sh
```

## Assessment and Feedback

### Rubrics for Each Exercise Type

#### Design Exercises
- Architecture completeness
- Trade-off analysis quality
- Documentation clarity
- Feasibility

#### Implementation Exercises  
- Code correctness
- Performance
- Error handling
- Test coverage

#### Analysis Exercises
- Calculation accuracy
- Interpretation depth
- Visualization quality
- Insights generated

### Automated Feedback Where Possible
```python
def check_solution(student_impl):
    score = 0
    feedback = []
    
    # Correctness
    if passes_tests(student_impl):
        score += 40
    else:
        feedback.append("Some tests failing - check edge cases")
    
    # Performance
    perf = measure_performance(student_impl)
    if perf < TARGET_LATENCY:
        score += 30
    else:
        feedback.append(f"Performance {perf}ms exceeds target {TARGET_LATENCY}ms")
    
    return score, feedback
```

## Maintenance

### Regular Updates
- Update with new real-world examples quarterly
- Refresh data sets annually  
- Add new exercises based on student feedback
- Remove outdated scenarios

### Version Control
```markdown
<!-- 
Exercise Version: 1.2
Last Updated: 2024-01-15
Changes: Updated latency numbers for 5G networks
-->
```

## Contributing New Exercises

1. Choose appropriate template
2. Copy template to new file
3. Fill in all sections
4. Test exercises yourself
5. Have colleague review
6. Submit PR with:
   - Completed exercise file
   - Any supporting files (data, code)
   - Update to navigation

## Examples of Excellence

Study these well-crafted exercises:
- `/docs/part2-pillars/state/exercises.md` - Comprehensive pillar exercises
- `/docs/quantitative/problem-set.md` - Clear quantitative problems
- `/docs/patterns/retry-backoff.md` - Detailed implementation example

## Quick Reference

### Exercise Types by Learning Goal

| Goal | Exercise Type | Example |
|------|---------------|---------|
| Understand constraints | Axiom Lab | Measure network latency |
| Design systems | Pillar Design | Architect state management |
| Implement solutions | Pattern Workshop | Build circuit breaker |
| Analyze performance | Quantitative | Calculate queue lengths |
| Debug problems | Pattern Debug | Fix broken implementation |
| Make decisions | Trade-off Analysis | Choose between patterns |

### Time Allocation Guidelines

| Exercise Type | Minimum | Typical | Maximum |
|---------------|---------|---------|---------|
| Quick Lab | 15 min | 30 min | 45 min |
| Implementation | 45 min | 90 min | 3 hours |
| Design Problem | 60 min | 2 hours | 4 hours |
| Analysis | 30 min | 60 min | 90 min |
| Project | 4 hours | 1 week | 2 weeks |

Remember: The goal is not just to test knowledge, but to build engineering intuition and practical skills that transfer to real-world distributed systems challenges.