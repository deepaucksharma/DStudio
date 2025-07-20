# Exercise Template: Patterns

This template provides practical, implementation-focused exercises for all pattern content.

## Structure

```markdown
# [Pattern Name] Exercises

## 🛠️ Implementation Workshops

### Workshop 1: [Basic Pattern Implementation]
**Difficulty**: ⭐⭐ (Beginner)
**Time**: 60 minutes
**Prerequisites**: Basic programming knowledge

#### Objective
Implement a basic version of [pattern] to understand core concepts.

#### Starter Project Structure
```
pattern-workshop/
├── src/
│   ├── __init__.py
│   ├── pattern_core.py      # TODO: Implement pattern
│   ├── client.py            # TODO: Client usage
│   └── tests.py             # Pre-written tests
├── requirements.txt
└── README.md
```

#### Step-by-Step Tasks

##### Task 1: Core Pattern Structure (20 min)
```python
# pattern_core.py
class PatternImplementation:
    """TODO: Implement the basic pattern structure"""
    
    def __init__(self):
        # TODO: Initialize pattern components
        pass
    
    def operation(self):
        # TODO: Implement core pattern operation
        pass
```

**Success Criteria**:
- [ ] Tests in `test_basic_structure.py` pass
- [ ] Pattern follows standard structure
- [ ] Clear separation of concerns

##### Task 2: Add Pattern Features (20 min)
Enhance your implementation with:
- [ ] Feature A: [specific feature]
- [ ] Feature B: [specific feature]
- [ ] Feature C: [specific feature]

##### Task 3: Client Integration (20 min)
```python
# client.py
def demo_pattern_usage():
    """TODO: Demonstrate pattern usage"""
    # Create pattern instance
    # Use pattern for specific scenario
    # Handle edge cases
    pass
```

#### Validation
Run the test suite:
```bash
python -m pytest tests.py -v
```

All tests should pass and coverage should be >90%.

<details>
<summary>Reference Implementation</summary>

[Complete implementation with detailed comments]
</details>

### Workshop 2: [Pattern with Real Infrastructure]
**Difficulty**: ⭐⭐⭐ (Intermediate)
**Time**: 90 minutes
**Prerequisites**: Docker, basic distributed systems knowledge

#### Setup
```bash
# Clone workshop repository
git clone [workshop-repo]
cd pattern-infrastructure-workshop

# Start infrastructure
docker-compose up -d
```

#### Infrastructure Provided
- Redis for state management
- PostgreSQL for persistence  
- RabbitMQ for messaging
- Monitoring stack (Prometheus + Grafana)

#### Your Task
Implement [pattern] that:
1. Integrates with provided infrastructure
2. Handles concurrent requests
3. Survives infrastructure failures
4. Provides monitoring metrics

[Detailed implementation steps...]

## 🔧 Debugging Challenges

### Challenge 1: [Fix the Broken Pattern]
**Difficulty**: ⭐⭐⭐ (Intermediate)
**Time**: 45 minutes

#### Scenario
A junior developer implemented [pattern] but it has several bugs:

```python
# broken_pattern.py
class BrokenPattern:
    # This implementation has 5 bugs that violate pattern principles
    def __init__(self):
        self.state = []  # Bug 1: Wrong data structure
        
    def operation(self, request):
        # Bug 2: Missing validation
        result = self.process(request)
        # Bug 3: Not thread-safe
        self.state.append(result)
        # Bug 4: Missing error handling
        return result
    
    def process(self, request):
        # Bug 5: Incorrect algorithm
        return request * 2
```

#### Your Tasks
1. Identify all 5 bugs
2. Explain why each violates pattern principles
3. Fix the implementation
4. Add tests to prevent regression

<details>
<summary>Bug Analysis and Fixes</summary>

[Detailed explanation of each bug and proper fix]
</details>

### Challenge 2: [Performance Debugging]
**Difficulty**: ⭐⭐⭐⭐ (Advanced)
**Time**: 60 minutes

#### Setup
```python
# slow_pattern.py
# This pattern implementation is functionally correct but has 
# severe performance issues under load
```

#### Performance Requirements
- Handle 10,000 requests/second
- p99 latency < 100ms
- Memory usage < 500MB

#### Tools Provided
- Load testing script
- Profiler setup
- Monitoring dashboard

#### Your Task
1. Run load test and identify bottlenecks
2. Profile the implementation
3. Optimize without breaking functionality
4. Verify improvements

## 🏗️ Design Exercises

### Exercise 1: [Pattern Selection]
**Time**: 30 minutes
**Format**: Decision matrix

#### Scenario
You're designing [specific system]. Multiple patterns could work:
- Pattern A: [pattern name]
- Pattern B: [pattern name]  
- Pattern C: [pattern name]

#### Requirements
[List of specific requirements with metrics]

#### Your Task
Create a decision matrix:

| Criteria | Weight | Pattern A | Pattern B | Pattern C |
|----------|---------|-----------|-----------|-----------|
| Performance | 30% | | | |
| Complexity | 20% | | | |
| Maintenance | 20% | | | |
| Scalability | 20% | | | |
| Cost | 10% | | | |
| **Total Score** | | | | |

Justify your scoring and recommend a pattern.

### Exercise 2: [Pattern Composition]
**Time**: 60 minutes
**Difficulty**: ⭐⭐⭐⭐ (Advanced)

#### Challenge
Design a system that combines:
- [Pattern 1] for [purpose]
- [Pattern 2] for [purpose]
- [Pattern 3] for [purpose]

#### Constraints
- Patterns must not conflict
- System must remain maintainable
- Performance targets must be met

#### Deliverables
1. Architecture diagram showing pattern integration
2. Sequence diagram for key operation
3. Analysis of pattern interactions
4. Potential conflict resolution

## 📊 Performance Labs

### Lab 1: [Pattern Benchmarking]
**Time**: 45 minutes
**Tools**: Provided benchmarking harness

#### Setup
```python
# benchmark_harness.py
class PatternBenchmark:
    def __init__(self, pattern_impl):
        self.pattern = pattern_impl
        self.results = {}
    
    def run_benchmarks(self):
        # TODO: Implement benchmarks
        pass
```

#### Benchmarks to Implement
1. **Throughput Test**: Max requests/second
2. **Latency Test**: p50, p95, p99 under load
3. **Scalability Test**: Performance vs. concurrent clients
4. **Memory Test**: Memory usage under sustained load

#### Tasks
1. Implement benchmark suite
2. Run against reference implementation
3. Run against your implementation
4. Compare results and explain differences

### Lab 2: [Pattern Under Stress]
**Time**: 60 minutes
**Difficulty**: ⭐⭐⭐⭐ (Advanced)

#### Chaos Engineering Scenarios
1. **Network Partition**: Pattern behavior during network split
2. **Resource Exhaustion**: Pattern behavior when resources depleted
3. **Cascading Failure**: Pattern's role in preventing cascade
4. **Thunder Herd**: Pattern's behavior during synchronized load

#### Your Task
For each scenario:
1. Predict pattern behavior
2. Run chaos test
3. Analyze actual behavior
4. Propose improvements

## 🌍 Real-World Case Studies

### Case Study 1: [Pattern at Scale]
**Company**: [Real company name]
**Context**: How they use [pattern] in production

#### Research Tasks
1. **Architecture Analysis**
   - Read their engineering blog posts
   - Analyze published architecture diagrams
   - Identify pattern usage

2. **Implementation Details**
   - Specific technologies used
   - Customizations made
   - Scale achieved

3. **Lessons Learned**
   - What worked well
   - What challenges they faced
   - How they evolved the pattern

#### Deliverable
2-page analysis with:
- Architecture diagram (recreated)
- Key insights
- Applicability to other contexts

### Case Study 2: [Pattern Evolution]
**Task**: Trace how [pattern] evolved at [company] over 5 years

[Similar structure with focus on evolution]

## 🎯 Testing Mastery

### Exercise 1: [Test the Pattern]
**Time**: 45 minutes
**Objective**: Write comprehensive tests for pattern implementation

#### Test Categories Required
```python
# test_pattern_comprehensive.py

class TestPatternCore:
    """Test basic pattern functionality"""
    def test_happy_path(self):
        # TODO
        pass
    
    def test_edge_cases(self):
        # TODO
        pass

class TestPatternConcurrency:
    """Test pattern under concurrent access"""
    def test_thread_safety(self):
        # TODO
        pass
    
    def test_race_conditions(self):
        # TODO
        pass

class TestPatternFailure:
    """Test pattern failure handling"""
    def test_graceful_degradation(self):
        # TODO
        pass
    
    def test_recovery(self):
        # TODO
        pass

class TestPatternPerformance:
    """Test pattern performance characteristics"""
    def test_latency_bounds(self):
        # TODO
        pass
    
    def test_throughput(self):
        # TODO
        pass
```

#### Success Criteria
- [ ] 100% code coverage
- [ ] Tests are deterministic
- [ ] Tests complete in < 30 seconds
- [ ] Edge cases covered
- [ ] Failure modes tested

### Exercise 2: [Property-Based Testing]
**Time**: 60 minutes
**Difficulty**: ⭐⭐⭐⭐ (Advanced)

Using Hypothesis or similar:
```python
from hypothesis import given, strategies as st

class TestPatternProperties:
    @given(st.lists(st.integers()))
    def test_pattern_invariant(self, inputs):
        """Pattern should maintain invariant X regardless of input"""
        # TODO
        pass
```

## 🚀 Production Readiness

### Checklist Exercise
**Time**: 90 minutes
**Objective**: Prepare pattern for production deployment

#### Production Checklist
- [ ] **Observability**
  - [ ] Metrics exported
  - [ ] Distributed tracing integrated
  - [ ] Structured logging implemented
  - [ ] Alerts configured

- [ ] **Reliability**
  - [ ] Circuit breakers added
  - [ ] Timeouts configured
  - [ ] Retries implemented
  - [ ] Graceful degradation

- [ ] **Performance**
  - [ ] Load tested to 2x expected traffic
  - [ ] Resource limits set
  - [ ] Caching strategy implemented
  - [ ] Database queries optimized

- [ ] **Security**
  - [ ] Input validation
  - [ ] Authentication/authorization
  - [ ] Encryption in transit
  - [ ] Secrets management

- [ ] **Operations**
  - [ ] Deployment automation
  - [ ] Rollback procedure
  - [ ] Runbook documentation
  - [ ] Monitoring dashboard

#### Your Task
Take your pattern implementation and make it production-ready by addressing each checklist item.

## 📚 Learning Path

### Week 1: Understanding
- [ ] Complete basic implementation workshop
- [ ] Fix broken pattern challenge
- [ ] Write comprehensive tests

### Week 2: Application  
- [ ] Complete infrastructure workshop
- [ ] Do performance debugging
- [ ] Implement benchmarks

### Week 3: Mastery
- [ ] Complete production checklist
- [ ] Analyze real-world case study
- [ ] Design pattern composition

### Week 4: Innovation
- [ ] Extend pattern for new use case
- [ ] Contribute to open source
- [ ] Write blog post about learnings
```

## Usage Guidelines

1. **Hands-On First**: Start with implementation, then move to theory
2. **Use Real Tools**: Docker, monitoring, load testing - not toy examples
3. **Focus on Debugging**: Engineers spend more time debugging than writing
4. **Production Context**: Every exercise should consider production concerns
5. **Provide Infrastructure**: Don't make students set up complex environments
6. **Clear Success Criteria**: Students should know when they've succeeded
7. **Build Portfolio**: Exercises should produce showcase-worthy work

## Quality Checklist

- [ ] Multiple implementation exercises with increasing complexity
- [ ] Debugging and troubleshooting scenarios
- [ ] Performance and stress testing components
- [ ] Real-world case study analysis
- [ ] Production readiness considerations
- [ ] Clear progression path
- [ ] Automated testing for validation
- [ ] Infrastructure provided via Docker
- [ ] Reference implementations available
- [ ] Connection to other patterns shown