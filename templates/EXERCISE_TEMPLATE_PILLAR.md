# Exercise Template: Pillars

This template ensures comprehensive, practical exercises for all pillar content.

## Structure

```markdown
# [Pillar Name] Exercises

## 🏗️ System Design Exercises

### Exercise 1: [Design from Scratch]
**Difficulty**: ⭐⭐⭐ (Intermediate)
**Time**: 90 minutes
**Format**: Individual or Pair

#### Scenario
You're the lead architect for [specific company/project]. They need a system that [specific requirements].

#### Constraints
- **Scale**: [Specific numbers - users, requests/sec, data volume]
- **Performance**: [Latency requirements, throughput needs]
- **Reliability**: [Uptime SLA, data durability]
- **Budget**: [Cost constraints]
- **Team**: [Team size and expertise]

#### Requirements
1. **Functional Requirements**:
   - [ ] Requirement 1 with specific metrics
   - [ ] Requirement 2 with specific metrics
   - [ ] Requirement 3 with specific metrics

2. **Non-Functional Requirements**:
   - [ ] Availability: [specific SLA]
   - [ ] Latency: [specific p50/p99]
   - [ ] Scalability: [growth projections]

#### Deliverables
1. **Architecture Diagram** (use Mermaid)
2. **Design Document** covering:
   - Component responsibilities
   - Data flow
   - Failure handling
   - Trade-off decisions
3. **Capacity Planning** calculations
4. **Cost Estimation**

#### Evaluation Rubric
| Aspect | Excellent (4) | Good (3) | Adequate (2) | Needs Work (1) |
|--------|---------------|----------|---------------|----------------|
| Pillar Application | Masterfully applies pillar concepts | Correctly applies core concepts | Basic understanding shown | Misses key concepts |
| Trade-off Analysis | Clear quantified decisions | Good reasoning | Some analysis | Minimal justification |
| Practicality | Production-ready design | Mostly realistic | Some impractical elements | Unrealistic |
| Documentation | Clear, complete, professional | Well documented | Adequate docs | Poor documentation |

<details>
<summary>Reference Solution</summary>

### Architecture Overview
```mermaid
graph TB
    [Architecture diagram]
```

### Key Design Decisions
1. **Decision 1**: Chose X because Y
   - Trade-off: Gained A, sacrificed B
   - Quantified impact: [metrics]

2. **Decision 2**: [Similar format]

### Capacity Planning
```python
# Calculations showing work
users = 1_000_000
requests_per_user_per_day = 100
...
```

### Implementation Plan
[Phased approach with milestones]
</details>

### Exercise 2: [Improving Existing System]
**Difficulty**: ⭐⭐⭐⭐ (Advanced)
**Time**: 2 hours
**Format**: Team of 3-4

#### Current System
[Detailed description of problematic system]

```mermaid
graph LR
    [Current architecture diagram]
```

#### Problems
1. [Specific problem with metrics]
2. [Specific problem with metrics]
3. [Specific problem with metrics]

#### Your Task
Redesign the system to address these problems while:
- Maintaining backward compatibility
- Minimizing migration risk
- Staying within budget
- Using existing team skills

[Rest follows similar structure to Exercise 1]

## 💻 Implementation Projects

### Project 1: [Build a Mini Version]
**Difficulty**: ⭐⭐⭐ (Intermediate)
**Time**: 4-6 hours
**Language**: Python (or student choice)

#### Objective
Build a working implementation that demonstrates [pillar concept].

#### Specifications
```yaml
functional_requirements:
  - Feature 1: [specific behavior]
  - Feature 2: [specific behavior]
  
performance_requirements:
  - Throughput: X operations/second
  - Latency: < Y milliseconds
  - Memory: < Z MB
  
quality_requirements:
  - Test coverage: > 80%
  - Documentation: API docs required
  - Error handling: Graceful degradation
```

#### Starter Code
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import asyncio

@dataclass
class Request:
    # TODO: Define request structure
    pass

class PillarImplementation(ABC):
    """Base class for your implementation"""
    
    @abstractmethod
    async def process(self, request: Request) -> Response:
        """Process a request according to pillar principles"""
        pass
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, float]:
        """Return current performance metrics"""
        pass

# TODO: Implement your solution
class YourImplementation(PillarImplementation):
    def __init__(self):
        pass

# Test harness
async def test_implementation(impl: PillarImplementation):
    # TODO: Run performance tests
    pass

if __name__ == "__main__":
    impl = YourImplementation()
    asyncio.run(test_implementation(impl))
```

#### Test Cases
```python
def test_basic_functionality():
    # TODO: Implement
    pass

def test_performance():
    # TODO: Implement
    pass

def test_failure_handling():
    # TODO: Implement
    pass
```

<details>
<summary>Reference Implementation</summary>

[Complete working implementation with comments explaining pillar applications]
</details>

### Project 2: [Production Feature]
**Difficulty**: ⭐⭐⭐⭐⭐ (Expert)
**Time**: 8-12 hours
**Format**: Team project

[Similar structure but more complex, potentially multi-service]

## 🔍 Analysis Exercises

### Exercise 1: [Pillar in the Wild]
**Objective**: Analyze how real companies apply this pillar

#### Part A: Research (2 hours)
Select one of these systems:
- Netflix's [relevant system]
- Uber's [relevant system]
- Amazon's [relevant system]

Research and document:
1. How they apply [pillar] principles
2. Specific techniques and patterns used
3. Published metrics and results
4. Evolution over time

#### Part B: Comparison (1 hour)
Create a comparison matrix:

| Aspect | Company 1 | Company 2 | Company 3 |
|--------|-----------|-----------|-----------|
| Scale | | | |
| Approach | | | |
| Key Innovation | | | |
| Trade-offs | | | |
| Results | | | |

#### Part C: Recommendations (1 hour)
If you were consulting for a startup wanting to apply these lessons:
1. What would you recommend?
2. What would you avoid?
3. How would you phase the implementation?

### Exercise 2: [Failure Analysis]
**Objective**: Learn from systems that violated pillar principles

[Case study of actual failure with analysis framework]

## 🧠 Thought Leadership

### Essay Topic 1: [Future of the Pillar]
**Prompt**: In 2035, how will [emerging technology] change how we think about [pillar]?

**Requirements**:
- 1000-1500 words
- At least 5 citations
- Consider multiple perspectives
- Include quantitative predictions

### Essay Topic 2: [Challenging the Pillar]
**Prompt**: Under what circumstances might violating [pillar] principles actually be the right choice?

[Similar requirements]

## 🎮 Simulation Exercise

### [Pillar] Game
**Format**: Interactive simulation
**Time**: 45 minutes
**Players**: 2-4

#### Setup
[Description of simulation/game that teaches pillar concepts through play]

#### Rules
1. [Game mechanics that reinforce pillar principles]
2. [Scoring system based on correct application]
3. [Failure conditions that demonstrate violations]

#### Debrief Questions
- What strategies worked best?
- How did the game mechanics relate to real systems?
- What surprised you?

## 🏆 Capstone Challenge

### Build a [Pillar]-Optimized System
**Duration**: 1 week
**Format**: Individual or team

#### Challenge
Build a complete system that exemplifies mastery of [pillar] principles.

#### Requirements
1. **Functional**: [Specific features]
2. **Scale**: Must handle [specific load]
3. **Performance**: Must achieve [specific metrics]
4. **Reliability**: Must survive [specific failures]
5. **Documentation**: Architecture, trade-offs, operations guide

#### Evaluation
- Live demo with load testing
- Architecture review presentation
- Code review
- Documentation quality

#### Bonus Challenges
- [ ] Implement advanced feature X
- [ ] Achieve 10x performance target
- [ ] Zero-downtime deployment
- [ ] Multi-region deployment

## 📈 Progress Tracking

### Self-Assessment Checklist
Rate yourself 1-5 on each:
- [ ] I can explain [pillar] principles to others
- [ ] I can identify [pillar] patterns in existing systems
- [ ] I can design systems that leverage [pillar]
- [ ] I can implement [pillar] concepts in code
- [ ] I can make quantified trade-off decisions
- [ ] I can troubleshoot [pillar]-related issues

### Portfolio Pieces
Complete at least 3 to demonstrate proficiency:
- [ ] System design with detailed trade-off analysis
- [ ] Working implementation with performance tests
- [ ] Analysis of production system
- [ ] Essay on future directions
- [ ] Contribution to open source project
- [ ] Blog post explaining concept to beginners

## 🔗 Connections

### How This Pillar Relates to Others
Create a mind map showing relationships:
- Dependencies on other pillars
- Conflicts with other pillars
- Synergies with other pillars

### Integration Exercise
Design a system that must balance [this pillar] with [another pillar].
Document the tensions and resolutions.
```

## Usage Guidelines

1. **Focus on Real-World Application**: Every exercise should mirror actual engineering challenges
2. **Provide Clear Constraints**: Specific numbers and requirements, not vague descriptions
3. **Scaffold Complexity**: Build from simple to complex within each section
4. **Include Team Exercises**: Distributed systems require collaboration
5. **Emphasize Documentation**: Clear communication is as important as implementation
6. **Connect to Production**: Use real company examples and published architectures
7. **Support Multiple Solutions**: Acknowledge trade-offs rather than one "right" answer

## Quality Checklist

- [ ] Mix of design, implementation, and analysis exercises
- [ ] Clear time estimates for each exercise
- [ ] Specific, measurable requirements
- [ ] Rubrics for evaluation
- [ ] Team and individual options
- [ ] Progressive difficulty levels
- [ ] Real-world constraints and scenarios
- [ ] Hidden solutions with explanations
- [ ] Connection to other pillars
- [ ] Portfolio-worthy deliverables