# Trade-off Calculus Radar

## The Extended Trade-off Dimensions

```
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

```
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