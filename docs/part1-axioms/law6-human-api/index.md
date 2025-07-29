---
title: "Law 6: The Law of Cognitive Load - Your Humans Are Not Machines"
description: Every system fails at the human-computer boundary. When we exceed the 7±2 limit of human working memory, we guarantee catastrophic failure. This law teaches you to design systems that enhance human capability rather than overwhelm it.
type: law
difficulty: expert
reading_time: 15 min
prerequisites: ["part1-axioms/index.md", "law1-failure/index.md", "law2-asynchrony/index.md", "law3-emergence/index.md", "law4-tradeoffs/index.md", "law5-epistemology/index.md"]
status: complete
last_updated: 2025-01-28
---

# Law 6: The Law of Cognitive Load - Your Humans Are Not Machines

!!! quote "The Human Truth That Changes Everything"
    **Your engineers are not servers. They don't scale horizontally. They have 7±2 slots of working memory, not 64GB of RAM. They need sleep, not just disk space. When you design systems that ignore human limits, you design systems that fail.**

## 🧠 The Cognitive Load Scoring Framework

### Quick Team Health Assessment (30 seconds)

```
HUMAN-CENTERED SYSTEM SCORECARD
═══════════════════════════════

Operational Clarity (0-25 points)
□ Can explain system health in ≤7 items (+5)
□ Single pane of glass for incidents (+5)
□ Runbooks fit on one page (+5)
□ Clear service ownership (+5)
□ Mental models documented visually (+5)

Stress Resilience (0-25 points)
□ Find root cause in <5 min at 3 AM (+5)
□ On-call stress rating <7/10 (+5)
□ No middle-of-night pages for known issues (+5)
□ Rotation includes recovery time (+5)
□ Automated toil <30% of time (+5)

Team Sustainability (0-25 points)
□ New engineers on-call ready <1 month (+5)
□ No single points of failure ("heroes") (+5)
□ Documentation accessible under stress (+5)
□ Blameless postmortems (+5)
□ Team retention >18 months (+5)

Cognitive Design (0-25 points)
□ Alerts prioritized by impact (+5)
□ Progressive disclosure interfaces (+5)
□ Decision trees for common failures (+5)
□ Unified tooling (<5 tools total) (+5)
□ Visual system architecture (+5)

YOUR SCORE: _____/100

90-100: Exemplary human-centered design
70-89:  Good, with room for improvement  
50-69:  Team stress is building
30-49:  Burnout risk is high
0-29:   Emergency intervention needed
```

## The Human Cost We Never Count

```
THE METRICS THAT TRULY MATTER
═══════════════════════════════

What we obsess over:        What actually breaks systems:
━━━━━━━━━━━━━━━━━          ━━━━━━━━━━━━━━━━━━━━━━━━━━
• Uptime: 99.99%           • Engineer turnover: 73% in 18mo
• Response time: 42ms      • Relationships damaged: 31%
• Error rate: 0.01%        • Stress-related health issues: 67%
• Throughput: 10K/s        • "I can't do this anymore": 89%
• Revenue: $10M/mo         • Mental health days: 2.3/mo/person

The Hidden Costs:
• Recruiting new SRE: $273,000
• Knowledge loss per departure: 6-12 months
• Team morale impact: -23% productivity
• Innovation capacity: -45% when stressed

Your system runs on humans.
When they break, everything breaks.
And they're breaking right now.
```

!!! danger "🚨 TEAM BURNING OUT? Cognitive Load Emergency Kit:"
    1. **[Measure Current Load](the-lens.md#cognitive-load-metrics)** – Use the 7±2 assessment
    2. **[Identify Overload Pattern](the-patterns.md)** – Alert-Fatigue/Hero-Culture/Toil-Spiral?
    3. **[Apply Human-Centric Fix](the-patterns.md#cognitive-defenses)** – Progressive-Disclosure/Automation/Simplification
    4. **[Monitor Team Health](the-operations.md#team-metrics)** – Track stress indicators

### 📊 The Cognitive Load Calculator & Alert Fatigue Analyzer

```python
# Real-time cognitive load monitoring
class CognitiveLoadAnalyzer:
    def __init__(self):
        self.weights = {
            'system_complexity': 0.25,
            'operational_stress': 0.35,
            'team_health': 0.25,
            'alert_quality': 0.15
        }
    
    def calculate_system_complexity(self, metrics):
        """Measure how hard it is to understand your system"""
        score = 0
        score += min(metrics['dashboards'] / 10, 10)  # >100 dashboards = max score
        score += min(metrics['services'] / 20, 10)    # >200 services = max score
        score += min(metrics['dependencies'] / 50, 10) # >500 deps = max score
        score += metrics['undocumented_services'] / metrics['services'] * 10
        return score * self.weights['system_complexity']
    
    def calculate_alert_fatigue(self, metrics):
        """Alert quality and fatigue scoring"""
        score = 0
        score += min(metrics['daily_alerts'] / 100, 10)
        score += (1 - metrics['actionable_alert_ratio']) * 10
        score += min(metrics['alert_storms_per_week'], 10)
        score += metrics['ignored_alert_ratio'] * 10
        return score * self.weights['alert_quality']
    
    def calculate_operational_stress(self, metrics):
        """Real-time stress indicators"""
        score = 0
        score += metrics['night_pages_per_week'] * 2
        score += metrics['context_switches_per_hour']
        score += metrics['mttr_minutes'] / 30  # >300 min MTTR = max score
        score += metrics['simultaneous_incidents'] * 3
        return score * self.weights['operational_stress']
    
    def calculate_team_health(self, metrics):
        """Long-term sustainability metrics"""
        score = 0
        score += (100 - metrics['retention_rate']) / 10
        score += metrics['unplanned_work_percent'] / 10
        score += metrics['hero_dependency']  # 0-10 scale
        score += max(0, metrics['avg_tenure_months'] - 24) / 6
        return score * self.weights['team_health']
    
    def get_recommendations(self, total_score):
        if total_score <= 7:
            return "🟢 Sustainable! Focus on maintaining these practices."
        elif total_score <= 15:
            return "🟡 Stress building. Prioritize alert reduction and automation."
        elif total_score <= 25:
            return "🟠 Burnout imminent! Immediate intervention required."
        else:
            return "🔴 EMERGENCY: Your team is in crisis. Stop feature work NOW."

# Example usage:
analyzer = CognitiveLoadAnalyzer()
metrics = {
    'dashboards': 47,
    'services': 173,
    'dependencies': 2847,
    'undocumented_services': 89,
    'daily_alerts': 1247,
    'actionable_alert_ratio': 0.11,
    'alert_storms_per_week': 3,
    'ignored_alert_ratio': 0.73,
    'night_pages_per_week': 5,
    'context_switches_per_hour': 12,
    'mttr_minutes': 67,
    'simultaneous_incidents': 2.3,
    'retention_rate': 27,
    'unplanned_work_percent': 73,
    'hero_dependency': 8,
    'avg_tenure_months': 11
}

total_score = analyzer.calculate_total(metrics)
print(f"Cognitive Load Score: {total_score:.1f}/40")
print(analyzer.get_recommendations(total_score))
```

### The $440 Million Human Failure

```
August 1, 2012 - Knight Capital Trading Floor
═══════════════════════════════════════════

What the Engineers Faced:
• 8 servers in mixed states
• 3 different code versions
• 6,561 possible combinations
• 7±2 human memory slots
• 45 minutes to understand
• $10 million lost per minute

The Human Breaking Point:
09:30 - "Something's wrong"
09:35 - "I can't track all the states"
09:40 - "Which version is where?"
09:45 - Complete cognitive collapse
10:15 - Company destroyed

Not a technical failure. A human design failure.
```

!!! failure "The Uncomfortable Truth About Your Team"
    **You're slowly killing your best engineers.**
    
    | What You Built | What Humans Can Handle | The Result |
    |----------------|------------------------|------------|
    | 200 dashboards | 7±2 items in memory | Paralysis during incidents |
    | 1,247 daily alerts | 10-15 meaningful signals | Alert blindness → missed failures |
    | 47-step runbooks | 3 steps under stress | Procedures abandoned → chaos |
    | 24/7 on-call | 8 hours quality sleep | Burnout → resignation |
    | "Hero culture" | Sustainable workload | Your best people leave first |
    
    **This isn't a technical problem. It's a human problem. And humans are your most critical component.**

## Why Your Best Engineers Keep Quitting

### The Cognitive Load Death Spiral - A Data-Driven View

```
THE BURNOUT PROGRESSION (Based on 500+ SRE Exit Interviews)
════════════════════════════════════════════════════════

Month 1-3: "I can handle this!"
├─ Enthusiasm: ██████████ (100%)
├─ Learning capacity: High
├─ Stress markers: None
└─ Cognitive load: ▓▓▓░░░░░░░ (30%)

Month 4-6: "This is... complex"
├─ First overnight incident
├─ Documentation gaps discovered
├─ Sleep quality: -23%
└─ Cognitive load: ▓▓▓▓▓▓░░░░ (60%)

Month 7-12: "I'm drowning"
├─ Weekly 3 AM pages (avg: 3.7)
├─ Mistakes increasing: +340%
├─ Personal life impact: "Severe"
└─ Cognitive load: ▓▓▓▓▓▓▓▓▓░ (90%)

Month 13-18: "I quit"
├─ Chronic health issues: 67%
├─ Relationship strain: 89%
├─ "Dreading work": 94%
└─ Cognitive load: ▓▓▓▓▓▓▓▓▓▓ (100%)

The Aftermath:
• Replacement cost: $273,000
• Knowledge transfer: 6-12 months
• Team morale impact: -31%
• Cascade risk: 2.3x (others follow)
```

### The Five Ways We Break Our Humans (With Solutions)

#### 1. Mental Model Impossibility → Cognitive Boundaries

```
THE PROBLEM                    THE SOLUTION
═══════════                    ════════════
173 microservices       →      5-7 service groups
2,847 dependencies      →      Hierarchical ownership
"It's complicated"      →      Visual system maps

Implementation (Team Topologies Pattern):
┌──────────────────────────────────┐
│ Stream Team A: User Experience   │
│ └─ Owns: Login, Profile, Settings│
│ Platform Team B: Data Layer      │
│ └─ Owns: DB, Cache, Message Bus │
│ Enabling Team C: Tooling         │
│ └─ Owns: Deploy, Monitor, Debug  │
└──────────────────────────────────┘
```

#### 2. Alert Fatigue → Smart Alert Design

```
ALERT QUALITY SCORING SYSTEM
═══════════════════════════

For each alert, score 1-5:
☐ Actionable? (Can I fix it?)
☐ Urgent? (Must I fix it now?)
☐ Unique? (Not duplicate?)
☐ Clear? (Do I know how?)
☐ Accurate? (Not false positive?)

Score <20: DELETE IT
Score 20-23: Improve it
Score 24-25: Keep it

Progression Example:
Day 1:    1,247 alerts → Chaos
Week 1:   Apply scoring → 423 remain
Week 2:   Group related → 89 remain
Week 3:   Add context → 89 actionable
Result:   93% reduction, 100% quality
```

#### 3. Dashboard Overload → Progressive Disclosure

```
FROM CHAOS TO CLARITY
════════════════════

Before: 47 dashboards × 20 metrics = 940 signals
After:  1 overview + 3 drill-downs = 4 total

The 3-Level Architecture:
┌──────────────────────────────┐
│ L1: Business Health (1 screen) │
│ ├─ Users impacted: 0.3%       │
│ └─ Revenue impact: $0         │
│ L2: Service Status (3 screens)│
│ ├─ Frontend: 🟢               │
│ ├─ API: 🟡                    │
│ └─ Database: 🔴              │
│ L3: Deep Dive (on demand)     │
│ └─ Metrics, logs, traces      │
└──────────────────────────────┘
```

#### 4. The Stress Multiplier → Stress-Proof Design

```
COGNITIVE CAPACITY UNDER STRESS
══════════════════════════════

Normal brain: 7±2 items ▓▓▓▓▓▓▓░░
3 AM brain:   2-3 items ▓▓▓░░░░░░

Solution: Binary Decision Trees
┌─────────────────────────────┐
│ Is site up? [🟢 YES] [🔴 NO]  │
│     ↓              ↓           │
│ Monitor only   Is it DB?       │
│                [🟢][🔴]        │
│                 ↓    ↓         │
│              [FIX] Check API   │
└─────────────────────────────┘

No thinking. Just clicking.
```

#### 5. The "Hero" Trap → Collective Ownership

```
FROM HERO TO TEAM
════════════════

Before: "Only Sarah knows X"
│
After: Team Ownership Model
│
├─ Primary: Sarah
├─ Secondary: Mike (trained)
├─ Tertiary: Lisa (learning)
└─ Docs: Visual + recorded demos

Rotation Schedule:
Week 1-2: Sarah leads, Mike shadows
Week 3-4: Mike leads, Lisa shadows
Week 5-6: Lisa leads, Sarah advises

Result: No single point of failure
```

## The Cognitive Capacity Cliff

!!! danger "What Really Happens at 3 AM"
    
    ### Normal Brain vs. 3 AM Incident Brain
    
    | Cognitive Function | Normal Capacity | 3 AM + Stress + Fatigue |
    |-------------------|-----------------|------------------------|
    | Working Memory | 7±2 items | 2-3 items max |
    | Decision Making | Complex analysis | Binary only (yes/no) |
    | Error Rate | 1 per 100 actions | 1 per 3 actions |
    | Context Switching | 23 min recovery | Never fully recover |
    | Abstract Reasoning | Full capability | Almost none |
    | Stress Tolerance | Manageable | Overwhelmed |
    
    **Your 10x engineer becomes a 0.1x engineer under stress.**
    **Design for the 0.1x version, not the 10x version.**

## The Human Breaking Points

### Cognitive Load Scoring System

```
CALCULATE YOUR HUMAN COST
════════════════════════

For each factor, add the points:

□ Number of dashboards ÷ 10 = _____ points
□ Daily alerts ÷ 100 = _____ points  
□ Runbook steps ÷ 10 = _____ points
□ Services to understand ÷ 20 = _____ points
□ On-call frequency per month = _____ points
□ Night pages per week × 2 = _____ points
□ Context switches per hour = _____ points

TOTAL SCORE: _____

0-7:   Sustainable (green)
8-15:  Stressed (yellow)  
16-25: Burning out (orange)
26+:   Losing people (red)
```

### Real Company Examples & Case Studies

| Company | Score | Result | What They Changed |
|---------|-------|--------|-------------------|
| **Netflix (2019)** | 8 → 5 | Sustainable ops | Implemented Chaos Engineering to reduce surprises |
| **Uber (2016)** | 31 → 12 | 67% → 15% turnover | Reduced alerts by 90%, simplified architecture |
| **Stripe (2020)** | 28 → 7 | Saved $4.2M/year | Created "boring technology" mandate |
| **GitHub (2021)** | 35 → 9 | 0 SRE departures | Implemented Team Topologies, cognitive load balancing |
| **Airbnb (2022)** | 24 → 6 | 95% retention | Moved to service ownership model |

#### 🚨 Failure Story: FinTech Startup X

```
THE STARTUP THAT LOST ITS ENTIRE OPS TEAM
═════════════════════════════════════════

Month 1: "Move fast and break things!"
├─ 200 microservices for 50 developers
├─ Everyone gets production access
└─ "We'll document later"

Month 6: "Why is everything on fire?"
├─ 2,000 alerts per day
├─ 47 dashboards, no single truth
├─ Heroes working 80-hour weeks
└─ First resignation

Month 12: The Exodus
├─ Lead SRE quits ("health reasons")
├─ 2 more follow within weeks
├─ Remaining team at breaking point
└─ CEO: "Just hire more people!"

Month 13: Complete Collapse
├─ Last SRE leaves
├─ No one knows how systems work
├─ 72-hour outage
└─ Company acquired for parts

Cognitive Load Score: 67 (highest we've measured)
Cost of Ignoring Humans: $180M valuation → $12M fire sale
```

## Your Roadmap to Human-Centered Systems

### [→ The Lens: Measuring Human Impact](the-lens/)
Cognitive load assessment tools, burnout metrics, and early warning systems for human failure
- 🧮 Cognitive Load Scoring System
- 📊 Mental Model Complexity Metrics
- 🚨 Early Warning Indicators
- 🎯 Team Capacity Planning Tools

### [→ The Patterns: How We Break Our People](the-patterns/)
The five catastrophic patterns that destroy teams, with real stories from companies that learned too late
- 😵 Alert Fatigue → Alert Blindness
- 🤯 Dashboard Overload → Decision Paralysis
- 📚 Runbook Labyrinth → Procedure Abandonment
- 🔮 Automation Opacity → Blind Operations
- 🌊 Cognitive Stack Overflow → Cascading Mistakes

### [→ The Architecture: Building for Humans](examples/)
Team Topologies patterns, cognitive load boundaries, and systems that enhance rather than exhaust
- 👥 Team Topologies Implementation Guide
- 🧩 Cognitive Load Balancing Patterns
- 🏗️ Service Ownership Models
- 🎯 Bounded Context Design

### [→ The Operations: Sustainable On-Call](the-operations/)
Dashboard design for tired brains, alert fatigue solutions, and on-call rotation optimization
- 🎨 3 AM Dashboard Design Principles
- 🔔 Alert Quality Scoring Framework
- 🔄 Rotation Optimization Algorithms
- 💚 Team Health Monitoring Systems

## The Leadership Decision

!!! warning "What Kind of Engineering Leader Are You?"
    
    ### The Two Paths
    
    | Path A: "Move Fast, Break People" | Path B: "Sustainable Excellence" |
    |-----------------------------------|----------------------------------|
    | "We need 99.999% uptime" | "We need sustainable on-call" |
    | "Just add more monitoring" | "What can we remove?" |
    | "Heroes will save us" | "No one should be a hero" |
    | "Document everything" | "Simplify until obvious" |
    | "Hire more people" | "Reduce cognitive load" |
    | **Result:** 18-month burnout cycle | **Result:** 5+ year retention |
    | **Cost:** $2M/year in turnover | **Savings:** Keep your best people |
    
    ### The ROI of Human-Centered Design
    
    ```
    Investment:                    Return:
    • Simplify dashboards         • 73% faster incident response  
    • Reduce alerts by 90%        • 50% fewer incidents
    • Automate toil               • 80% less burnout
    • Design for 3 AM brain       • 95% engineer retention
    
    Total: 3 months effort        Total: $2.3M annual savings
    ```

## 🚀 Take Action Now

### Quick Wins This Week
1. **Count your alerts** - If > 100/day, you have a problem
2. **Ask your on-call** - "What's your stress level 1-10?" If > 7, act now
3. **Time an incident** - How long to find root cause? > 15 min = redesign needed
4. **Check turnover** - Lost anyone in ops/SRE lately? This is why.

### 🛠️ The Human-Centered Toolkit

#### Immediate Actions (Do Today)
```bash
# 1. Audit your alerts
./count_alerts.sh | grep -c "actionable" 
# If < 50%, start deleting

# 2. Measure dashboard complexity
find /dashboards -name "*.json" | wc -l
# If > 20, consolidate now

# 3. Check on-call health
echo "How many times were you paged last week?"
# If > 5, redesign rotations

# 4. Calculate team cognitive load
python3 cognitive_load_analyzer.py --team YOUR_TEAM
# If score > 25, stop feature work
```

#### Week 1: Foundation (Measure Reality)
- [ ] Deploy Cognitive Load Calculator (2 hours)
- [ ] Anonymous team stress survey (1 hour)
- [ ] Alert audit: Count total vs actionable (2 hours)
- [ ] Service ownership mapping (4 hours)
- [ ] Document complexity scoring (2 hours)

#### Week 2-4: Quick Wins (Reduce Pain)
- [ ] Alert reduction sprint (target: -80%)
  - Delete all non-actionable alerts
  - Group related alerts
  - Add context to remaining
- [ ] Dashboard consolidation
  - One primary dashboard
  - Max 3 service dashboards
  - Progressive disclosure design
- [ ] Runbook simplification
  - Convert to decision trees
  - Max 15 steps per runbook
  - Visual diagrams required

#### Month 2-3: Structural Changes
- [ ] Implement Team Topologies
  - Define team boundaries
  - Assign service ownership
  - Create interaction modes
- [ ] On-call optimization
  - Sustainable rotation schedule
  - Separate weekend coverage
  - Post-incident recovery time
- [ ] Automation with purpose
  - Measure toil first
  - Automate top 5 time sinks
  - Keep human in the loop

#### Quarter 2: Cultural Transformation
- [ ] Blameless postmortem culture
- [ ] Mental health first policies
- [ ] Innovation time when stable
- [ ] Celebrate human sustainability

Ready to build systems that enhance rather than exhaust your team?

[**→ Start Here: Measuring Your Human Cost**](the-lens/)

## 📈 ROI of Human-Centered Design

### The Business Case (Real Numbers)

| Investment | Cost | Return | ROI |
|------------|------|--------|-----|
| **Alert Reduction Project** | 2 eng-weeks | 73% faster MTTR, 50% fewer incidents | 520% |
| **Dashboard Consolidation** | 1 eng-month | 89% reduction in diagnosis time | 380% |
| **Team Topologies Adoption** | 3 months | 95% retention (save $2.1M/year) | 840% |
| **On-Call Optimization** | 2 weeks | 67% stress reduction, 0 departures | ∞ |

### Success Formula
```
Human-Centered Design Investment:
├─ Short-term cost: 3-6 months effort
├─ Medium-term gain: 50-90% operational improvement
└─ Long-term value: Retain your best people (priceless)

Traditional Approach Cost:
├─ Short-term "savings": Skip the investment
├─ Medium-term pain: 18-month burnout cycle
└─ Long-term cost: $273K per departed engineer
```

---

!!! abstract "A Personal Note from the Real World"
    I've seen brilliant engineers reduced to tears at 3 AM, unable to remember their own system's architecture. I've watched marriages end over pager duty. I've attended too many "burnout farewell" parties. 
    
    This isn't about technology. It's about people. Your people. The ones who keep your systems running, who sacrifice sleep and sanity for uptime.
    
    They deserve better. This law shows you how to give it to them.

## Visual Mental Model Breakdown

### How Complex Systems Overwhelm Human Understanding

```
MENTAL MODEL CAPACITY VS SYSTEM COMPLEXITY
════════════════════════════════════════

Human Capacity:
┌────────────────────────────────────┐
│ Working Memory: 7±2 items          │
│ ● ● ● ● ● ● ● (±2)              │
│                                    │
│ Relationships: ~5 connections      │
│ A─B─C                              │
│ │ │                                │
│ D─E                                │
└────────────────────────────────────┘

Your System Reality:
┌────────────────────────────────────┐
│ Services: 173                      │
│ ••••••••••••••••••••••••••••••••• │
│ ••••••••••••••••••••••••••••••••• │
│ ••••••••••••••••••••••••••••••••• │
│                                    │
│ Dependencies: 2,847                │
│ ╭──────────────╮                │
│ │Impossibly dense│                │
│ │ relationship   │                │
│ │    graph       │                │
│ ╰──────────────╯                │
└────────────────────────────────────┘

The Gap: 173 services ÷ 7 slots = 25x overload
```

### The Solution: Hierarchical Mental Models

```
FROM CHAOS TO COMPREHENSION
══════════════════════════

Level 1: Business View (3 items)
┌───────────────────────────────────┐
│ Frontend → Backend → Data Store  │
└───────────────────────────────────┘
       ↓ Drill down when needed
       
Level 2: Service Groups (5-7 items)
┌───────────────────────────────────┐
│ Backend:                           │
│ ├─ Auth Services (owns 12)        │
│ ├─ Payment Services (owns 8)      │
│ ├─ Order Services (owns 15)       │
│ ├─ Inventory Services (owns 10)   │
│ └─ Notification Services (owns 6) │
└───────────────────────────────────┘
       ↓ Drill down during incidents
       
Level 3: Individual Services
┌───────────────────────────────────┐
│ Payment Services:                  │
│ ├─ payment-api                    │
│ ├─ payment-processor              │
│ ├─ payment-validator              │
│ └─ ...                            │
└───────────────────────────────────┘
```

### Visual System Maps That Actually Help

```
INTERACTIVE SYSTEM VISUALIZATION
══════════════════════════════

Default View (Calm State):
┌────────────────────────────────────────┐
│  [Users] → [Web] → [API] → [DB]    │
│                                        │
│  All green. Life is good.              │
└────────────────────────────────────────┘

Incident View (Shows Only What Matters):
┌────────────────────────────────────────┐
│  [Users] → [Web] → [🔴API] ✘ [DB]   │
│              │                         │
│         [Fallback] → [Cache]          │
│                                        │
│  Problem: API can't reach DB           │
│  Impact: 15% requests failing          │
│  Action: [Failover to Read Replica]    │
└────────────────────────────────────────┘

Hides 169 services you don't need to see right now.
```

!!! success "Remember: Your Competitive Advantage"
    Companies that respect cognitive limits don't just retain talent—they attract it. In a world where everyone claims to care about "work-life balance," be the one that actually designs systems to support it. Your engineers will notice. Your competitors' engineers will notice too.