# Law 4: Exercises - The Trade-off Dojo 🥋

<div class="axiom-box">
<h2>Your Mission: Master the Art of Impossible Choices</h2>
<p>These exercises will rewire your brain to see trade-offs everywhere. By the end, you'll make peace with the fact that perfection is a lie—and that's exactly what makes you powerful.</p>
</div>

## Your Trade-off Readiness Test

```
CHECK YOUR LEVEL
═══════════════

□ Level 0: "We can have it all!"
□ Level 1: "OK, we need to choose..."
□ Level 2: "I see trade-offs in 2-3 dimensions"
□ Level 3: "I track 10+ dimensions"
□ Level 4: "I navigate trade-offs dynamically"
□ Level 5: "I profit from trade-offs"

Start wherever you are. Ascend to mastery.
```

---

## Exercise 1: The Trade-off Spotter 🔍

<div class="decision-box">
<h3>Warm-up: Find Hidden Trade-offs in "Perfect" Systems</h3>

Look at these "amazing" system claims. Identify the hidden trade-off:

```
CLAIM vs REALITY DETECTOR
════════════════════════

1. "Our database is ACID compliant AND massively scalable!"
   Hidden trade-off: _______________________

2. "Zero-downtime deployments with instant rollback!"
   Hidden trade-off: _______________________

3. "Bank-level security that's user-friendly!"
   Hidden trade-off: _______________________

4. "Serverless solution with predictable costs!"
   Hidden trade-off: _______________________

5. "Real-time analytics on petabytes of data!"
   Hidden trade-off: _______________________
```

<details>
<summary>🔓 Reveal the Hidden Trade-offs</summary>

```
THE UNCOMFORTABLE TRUTHS
═══════════════════════

1. ACID + Scale = $$$$ (Spanner) or Latency (2PC)
2. Zero-downtime = Complexity + Version Hell
3. Security + Friendly = Support Nightmare
4. Serverless + Predictable = Vendor Lock-in
5. Real-time + Petabytes = Approximation or Bankruptcy

Remember: Every "AND" hides an "OR"
```
</details>
</div>

---

## Exercise 2: Build Your Own CAP Triangle (But With 20 Dimensions) 📐

<div class="truth-box">
<h3>Task: Map Your System's Trade-off Space</h3>

```python
# YOUR SYSTEM'S TORTURE DEVICE
# ═══════════════════════════

class MySystemTradeoffs:
    def __init__(self, system_name):
        self.name = system_name
        self.dimensions = {}
        
    def add_dimension(self, name, current_value, max_value, unit):
        """Add a dimension you care about"""
        self.dimensions[name] = {
            'current': current_value,
            'max': max_value,
            'unit': unit,
            'cost_to_improve': self.calculate_cost(name)
        }
    
    def calculate_cost(self, dimension):
        """What do you sacrifice to improve this?"""
        # YOUR TASK: Fill this in for YOUR system
        costs = {
            'latency': ['throughput', 'cost'],
            'consistency': ['availability', 'latency'],
            'security': ['usability', 'performance'],
            # Add your dimensions...
        }
        return costs.get(dimension, [])
    
    def visualize_position(self):
        """Where are you in the space?"""
        # TODO: Create radar chart
        # Show current vs optimal
        pass

# EXERCISE: Map your production system
my_system = MySystemTradeoffs("My E-commerce Platform")

# Add at least 10 dimensions
my_system.add_dimension('page_load_time', 2.5, 0.5, 'seconds')
my_system.add_dimension('availability', 0.999, 0.99999, 'nines')
# ... add 8 more
```

**Reflection Questions:**
1. Which dimension is maxed out?
2. Which is completely ignored?
3. What would it cost to improve your worst dimension?
</div>

---

## Exercise 3: The Dynamic Trade-off Simulator 🎮

<div class="failure-vignette">
<h3>Scenario: Black Friday Is Coming!</h3>

Your e-commerce system normally handles 1,000 requests/second. Black Friday will bring 50,000 requests/second. You have 1 week to prepare.

```
YOUR CONTROL PANEL
═════════════════

Current Settings:
┌─────────────────────────────────┐
│ Consistency:    STRONG          │
│ Availability:   99.9%           │
│ Latency (p99):  100ms           │
│ Cache TTL:      60s             │
│ Replication:    3x              │
│ Cost/month:     $10,000         │
└─────────────────────────────────┘

Available Actions (each has consequences):
════════════════════════════════════════

A) Enable Eventual Consistency
   + Throughput: 10x
   - Consistency: Some users see old prices
   
B) Increase Cache TTL to 1 hour  
   + Throughput: 5x
   - Freshness: Sales might show wrong inventory
   
C) Add 10x More Servers
   + Throughput: 10x
   - Cost: $100,000 for the day
   
D) Implement Request Queuing
   + Availability: Won't crash
   - Latency: Some users wait 30+ seconds
   
E) Shed Non-Critical Features
   + Throughput: 3x
   - Revenue: No recommendations = -20% sales

YOUR MISSION: Combine actions to survive Black Friday
What's your strategy? (You can pick multiple)
```

<details>
<summary>💡 See Expert Solutions</summary>

```
EXPERT TRADE-OFF STRATEGIES
══════════════════════════

Strategy 1: "The Degraded Experience"
- Actions: A + B + E
- Result: Site stays up, slightly stale data
- Trade-off: Perfect accuracy for survival

Strategy 2: "The Big Spender"  
- Actions: C + small amounts of A
- Result: Nearly normal experience
- Trade-off: $$$ for quality

Strategy 3: "The Queue Master"
- Actions: D + B + smart load balancer
- Result: Everyone gets served eventually  
- Trade-off: Speed for completeness

REAL WORLD: Amazon does ALL of these:
- Degrades recommendations
- Increases cache aggressively  
- Pre-scales infrastructure
- Queues when needed
- Different paths for browse vs buy
```
</details>
</div>

---

## Exercise 4: The Pareto Frontier Finder 📊

<div class="axiom-box">
<h3>Challenge: Find Your System's Efficiency Frontier</h3>

```python
# THE PARETO OPTIMIZER
# ═══════════════════

def find_pareto_frontier(designs):
    """
    Find designs where you can't improve one dimension
    without making another worse
    """
    frontier = []
    
    for design in designs:
        dominated = False
        for other in designs:
            if all(other[dim] >= design[dim] for dim in dimensions) and \
               any(other[dim] > design[dim] for dim in dimensions):
                dominated = True
                break
        
        if not dominated:
            frontier.append(design)
    
    return frontier

# YOUR TASK: Evaluate these architectures
architectures = [
    {
        'name': 'Monolith PostgreSQL',
        'latency': 50,      # ms (lower better)
        'availability': 99.0,  # % (higher better)
        'cost': 1000,      # $/month (lower better)
        'complexity': 3    # 1-10 (lower better)
    },
    {
        'name': 'Microservices + Kafka',
        'latency': 100,
        'availability': 99.9,
        'cost': 5000,
        'complexity': 8
    },
    # Add 5 more architectures...
]

# Find your optimal choices
frontier = find_pareto_frontier(architectures)

# QUESTIONS:
# 1. Which architectures made the frontier?
# 2. Why didn't the others?
# 3. How would you choose between frontier options?
```

**Bonus**: Plot your frontier in 2D (pick any two dimensions) and see the trade-off curve!
</div>

---

## Exercise 5: The Multi-Tenant Negotiator 🤝

<div class="decision-box">
<h3>Scenario: Three Tenants, One Cluster, Infinite Arguments</h3>

```
THE RESOURCE ALLOCATION GAME
═══════════════════════════

Total Cluster Resources:
- 1000 CPU cores
- 10TB RAM  
- 100Gbps network
- $50,000/month budget

Tenant A: "The Startup"
- Needs: Cheap resources
- Wants: Burst capability
- Pays: $5,000/month
- SLA: 99% availability

Tenant B: "The Bank"
- Needs: Isolation
- Wants: Guaranteed resources
- Pays: $30,000/month
- SLA: 99.99% availability

Tenant C: "The AI Company"
- Needs: GPU access
- Wants: Maximum throughput
- Pays: $15,000/month
- SLA: Best effort

YOUR CHALLENGE: Design allocation strategy
```

```python
class ResourceAllocator:
    def __init__(self, total_resources):
        self.total = total_resources
        self.allocations = {}
    
    def propose_allocation(self, tenant, requested):
        """Propose resource allocation"""
        # YOUR TASK: Implement fair allocation
        # Consider:
        # - Payment proportion
        # - SLA requirements
        # - Resource efficiency
        # - Isolation needs
        pass
    
    def calculate_tenant_happiness(self, tenant, allocation):
        """How happy is tenant with allocation?"""
        # Implement happiness function
        # Consider: resources vs needs vs payment
        pass
    
    def find_nash_equilibrium(self):
        """Find stable allocation"""
        # Where no tenant wants to change
        pass

# Design your allocation strategy!
```

<details>
<summary>🎯 Solution Approaches</summary>

```
ALLOCATION STRATEGIES
════════════════════

1. "Strict Proportional"
   - Bank: 60% resources (pays 60%)
   - AI: 30% resources
   - Startup: 10% resources
   Problem: Startup unhappy, might leave

2. "SLA-Weighted"
   - Bank: 40% guaranteed + 20% burst
   - Startup: 5% guaranteed + 20% burst  
   - AI: 25% guaranteed + best effort
   Better: Meets SLAs, allows sharing

3. "Market-Based"
   - Spot pricing for unused resources
   - Bank gets reserved instances
   - Startup/AI bid for spare capacity
   Best: Efficient utilization

REAL WORLD: AWS/GCP use combination of all!
```
</details>
</div>

---

## Exercise 6: The Time-Shifted Trade-off Arbitrage ⏰

<div class="truth-box">
<h3>Challenge: Design Daily Trade-off Schedule</h3>

```
YOUR SYSTEM'S 24-HOUR CYCLE
══════════════════════════

00:00 ┼────────────────────────┤ 24:00
      │▓▓░░░░░░░░████░░░░▓▓▓▓▓│
      │└─Batch─┘ └Peak┘ └─Eve─┘│
      
Fill in optimal settings for each period:

BATCH WINDOW (00:00-06:00)
─────────────────────────
Traffic: 5% of peak
Optimize for: ____________
Settings:
- Consistency: ___________
- Batch size: ___________
- Replication: __________
- Cache TTL: ____________

BUSINESS HOURS (09:00-17:00)
───────────────────────────
Traffic: 100% of peak
Optimize for: ____________
Settings:
- Consistency: ___________
- Batch size: ___________
- Replication: __________
- Cache TTL: ____________

MAKE A PLAN: How do you transition between modes?
```

**Implementation Task:**
```python
class TimeBasedOptimizer:
    def __init__(self):
        self.schedules = {
            'night': {'optimize_for': 'throughput'},
            'morning': {'optimize_for': 'availability'},
            'peak': {'optimize_for': 'latency'},
            'evening': {'optimize_for': 'cost'}
        }
    
    def transition_safely(self, from_mode, to_mode):
        """Gradually shift between modes"""
        # YOUR TASK: Implement safe transitions
        # No sudden changes that break system!
        pass
```
</div>

---

## Exercise 7: The Trade-off Debt Calculator 💰

<div class="failure-vignette">
<h3>Quantify Your Technical Trade-off Debt</h3>

```
TRADE-OFF DEBT ASSESSMENT
════════════════════════

Just like technical debt, but for suboptimal trade-offs:

□ "We optimized for launch speed"
  Debt: _______________________
  Interest: ___________________

□ "We chose consistency over availability"  
  Debt: _______________________
  Interest: ___________________

□ "We picked the cheapest option"
  Debt: _______________________
  Interest: ___________________

Calculate your total:

def calculate_tradeoff_debt(decision):
    immediate_benefit = decision.saved_time
    ongoing_cost = decision.operational_overhead
    
    # Debt compounds!
    months_passed = get_months_since(decision.date)
    total_debt = ongoing_cost * (1.1 ** months_passed)
    
    return {
        'principal': immediate_benefit,
        'interest': total_debt - immediate_benefit,
        'monthly_payment': ongoing_cost,
        'bankruptcy_date': when_unsustainable()
    }

YOUR TASK: List your top 5 trade-off debts
Which will bankrupt you first?
```
</div>

---

## Exercise 8: The Production Trade-off Playbook 📖

<div class="axiom-box">
<h3>Build Your Emergency Trade-off Guide</h3>

Create runbooks for common scenarios:

```
SCENARIO: Database CPU at 90%
════════════════════════════

Option A: Scale Up (Easy)
├─ Time: 5 minutes
├─ Cost: +$1000/month
├─ Risk: None
└─ Reversal: Easy

Option B: Add Read Replicas (Medium)
├─ Time: 30 minutes  
├─ Cost: +$500/month
├─ Risk: Consistency issues
└─ Reversal: Complex

Option C: Enable Query Cache (Hard)
├─ Time: 2 hours
├─ Cost: +$100/month
├─ Risk: Stale data
└─ Reversal: Easy

YOUR DECISION TREE:
If revenue > $1M/day: Choose A
If consistency critical: Choose B  
If cost sensitive: Choose C

CREATE 5 MORE SCENARIOS:
1. Traffic spike
2. Region failure
3. Cost overrun
4. Security incident
5. Compliance audit
```
</div>

---

## Final Boss: Design a Self-Optimizing System 🤖

<div class="truth-box" style="background: #1a1a1a; border: 2px solid #ff5555;">
<h3>Ultimate Challenge: The Trade-off Autopilot</h3>

```python
class SelfOptimizingSystem:
    """
    System that navigates trade-off space autonomously
    """
    def __init__(self):
        self.current_position = {}
        self.target_slos = {}
        self.constraints = {}
        self.learning_rate = 0.1
        
    def sense_environment(self):
        """What's happening now?"""
        # TODO: Collect all metrics
        pass
        
    def predict_future(self):
        """What's about to happen?"""
        # TODO: Time series prediction
        # Detect patterns (daily, weekly)
        pass
        
    def generate_adaptations(self):
        """What could we change?"""
        # TODO: List all knobs
        # Predict impact of each
        pass
        
    def execute_adaptation(self, action):
        """Make the change safely"""
        # TODO: Gradual rollout
        # Monitor impact
        # Rollback if needed
        pass
        
    def learn_from_outcome(self, action, result):
        """Did it work?"""
        # TODO: Update model
        # Remember for next time
        pass

# YOUR CHALLENGE: Implement one complete adaptation cycle
# Example: Auto-scale read replicas based on query patterns
```

**Success Criteria:**
- System adapts without human intervention
- Never violates hard constraints
- Learns from its mistakes
- Explains its decisions
</div>

---

## Reflection & Synthesis

<div class="axiom-box">
<h3>The Trade-off Master's Checklist</h3>

After completing these exercises, you should be able to:

```
TRADE-OFF MASTERY CHECKLIST
══════════════════════════

□ See hidden trade-offs in any "perfect" solution
□ Map systems in 10+ dimensional space
□ Find Pareto optimal configurations
□ Design time-based optimization strategies
□ Calculate trade-off debt and interest
□ Build emergency trade-off playbooks
□ Negotiate multi-tenant resource allocation
□ Design self-adapting systems

If you checked all boxes, you're ready for:
THE REAL WORLD
Where every decision has a price,
And the price is always another decision.
```
</div>

## Your Homework

<div class="decision-box">
<h3>This Week's Mission</h3>

1. **Map your production system's trade-off space** (all dimensions)
2. **Find three hidden trade-offs** your team hasn't acknowledged
3. **Calculate your trade-off debt** in actual dollars
4. **Build one emergency playbook** for your most common incident
5. **Design one time-based optimization** for off-peak hours

Share your findings with your team.
Watch their minds explode. 🤯
</div>

---

**Remember**: The master doesn't eliminate trade-offs. The master dances with them.

**Next Law**: [Law 5: Distributed Knowledge](../law5-knowledge/) - Where truth becomes probability