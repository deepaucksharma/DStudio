---
title: Trade-off Calculus Radar
description: "Framework for analyzing and making architectural trade-offs in distributed systems"
type: pillar
difficulty: beginner
reading_time: 5 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part II: Pillars](/part2-pillars/) → **Trade-off Calculus Radar**

# Trade-off Calculus Radar

## The Extended Trade-off Dimensions

```text
                    Latency
                      0
                   2  .  4
               6    .   .   8
           10     .       .
    Security  .             . Capacity
        .       .         .
      .           . . .       .
    .                           .
Cost                              Availability
    .                           .
      .           . . .       .
        .       .         .
           .             .
              Complexity
```

## Calculating Your Position

```python
class TradeOffCalculator:
    def __init__(self):
        self.dimensions = {
            'latency': 0,      # 0=slow, 10=fast
            'capacity': 0,     # 0=low, 10=high
            'availability': 0, # 0=low, 10=high
            'complexity': 0,   # 0=simple, 10=complex
            'cost': 0,         # 0=expensive, 10=cheap
            'security': 0      # 0=weak, 10=strong
        }

    def add_pattern(self, pattern, impacts):
        """Add a pattern's impact on dimensions"""
        for dimension, impact in impacts.items():
            self.dimensions[dimension] += impact

    def normalize(self):
        """Normalize to 0-10 scale"""
        for dim in self.dimensions:
            self.dimensions[dim] = max(0, min(10, self.dimensions[dim]))

    def calculate_balance(self):
        """Higher score = more balanced system"""
        values = list(self.dimensions.values())
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return 10 - (variance ** 0.5)

    def recommend_improvement(self):
        """Suggest what to improve"""
        worst = min(self.dimensions.items(), key=lambda x: x[1])
        best = max(self.dimensions.items(), key=lambda x: x[1])

        return {
            'bottleneck': worst[0],
            'score': worst[1],
            'over_optimized': best[0],
            'potential_trade': f"Consider trading {best[0]} for {worst[0]}"
        }

# Example: E-commerce platform
platform = TradeOffCalculator()

# Current architecture
platform.add_pattern('microservices', {
    'latency': -2,      # Service calls
    'capacity': +3,     # Independent scaling
    'availability': +2, # Failure isolation
    'complexity': -3,   # Many moving parts
    'cost': -1,        # Overhead
    'security': +1     # Isolation
})

platform.add_pattern('caching', {
    'latency': +3,
    'capacity': +2,
    'availability': +1,
    'complexity': -1,
    'cost': +2,
    'security': -1  # Cache poisoning risk
})

platform.add_pattern('cdn', {
    'latency': +3,
    'capacity': +3,
    'availability': +2,
    'complexity': -1,
    'cost': -2,
    'security': +2
})

platform.normalize()
print("Current scores:", platform.dimensions)
print(f"Balance score: {platform.calculate_balance():.1f}/10")
print("Recommendation:", platform.recommend_improvement())
```

## Trade-off Patterns by Industry

```text
Financial Services:
Security ████████████ 10
Availability █████████ 9
Capacity ██████ 6
Latency ████ 4
Cost ██ 2
Complexity ████████ 8

Gaming Platform:
Latency ██████████ 10
Capacity ████████ 8
Availability ██████ 6
Security ████ 4
Cost ██████ 6
Complexity ██████ 6

Analytics Platform:
Capacity ██████████ 10
Cost █████████ 9
Complexity ████ 4
Latency ██ 2
Availability ████ 4
Security ██████ 6
```

---

**Next**: [Decision Tree Walk-Through →](decision-tree.md)
---

## 💡 Knowledge Application

### Exercise 1: Concept Exploration ⭐⭐
**Time**: ~15 minutes
**Objective**: Deepen understanding of Trade-off Calculus Radar

**Reflection Questions**:
1. What are the 3 most important concepts from this content?
2. How do these concepts relate to systems you work with?
3. What examples from your experience illustrate these ideas?
4. What questions do you still have?

**Application**: Choose one concept and explain it to someone else in your own words.

### Exercise 2: Real-World Connection ⭐⭐⭐
**Time**: ~20 minutes
**Objective**: Connect theory to practice

**Research Task**:
1. Find 2 real-world examples where these concepts apply
2. Analyze how the concepts manifest in each example
3. Identify what would happen if these principles were ignored

**Examples could be**:
- Open source projects
- Well-known tech companies
- Systems you use daily
- Historical technology decisions

### Exercise 3: Critical Thinking ⭐⭐⭐⭐
**Time**: ~25 minutes
**Objective**: Develop deeper analytical skills

**Challenge Scenarios**:
1. **Constraint Analysis**: What limitations or constraints affect applying these concepts?
2. **Trade-off Evaluation**: What trade-offs are involved in following these principles?
3. **Context Dependency**: In what situations might these concepts not apply?
4. **Evolution Prediction**: How might these concepts change as technology evolves?

**Deliverable**: A brief analysis addressing each scenario with specific examples.

---

## 🔗 Cross-Topic Connections

**Integration Exercise**:
- How does Trade-off Calculus Radar relate to other topics in this documentation?
- What patterns or themes do you see across different sections?
- Where do you see potential conflicts or tensions between different concepts?

**Systems Thinking**:
- How would you explain the role of these concepts in the broader context of distributed systems?
- What other knowledge areas complement what you've learned here?

---

## 🎯 Next Steps

**Immediate Actions**:
1. One thing you'll research further
2. One practice you'll try in your current work
3. One person you'll share this knowledge with

**Longer-term Learning**:
- What related topics would be valuable to study next?
- How will you stay current with developments in this area?
- What hands-on experience would solidify your understanding?

---
