# Reader Roadmap

## Choose Your Learning Path

<div class="metro-map">
  <svg viewBox="0 0 800 600" class="learning-paths">
    <!-- New Grad Line (Green) -->
    <path class="path-newgrad" d="M 50,50 L 150,50 L 250,100 L 350,100 L 450,150 L 550,150 L 650,200 L 750,200" />
    
    <!-- Senior IC Line (Blue) -->
    <path class="path-senior" d="M 50,150 L 200,150 L 350,200 L 500,200 L 650,250 L 750,250" />
    
    <!-- Manager Line (Orange) -->
    <path class="path-manager" d="M 50,250 L 150,250 L 250,300 L 400,300 L 550,350 L 750,350" />
    
    <!-- Express Route (Red) -->
    <path class="path-express" d="M 50,400 L 300,400 L 550,450 L 750,450" />
  </svg>
</div>

## New Graduate Line 🟢

**Journey Time**: 20-30 hours  
**Destination**: Strong distributed systems practitioner

### Your Stops:
1. **[START]** → Welcome & First Principles Framework
2. **Axioms 1-3** → Latency, Capacity, Failure (The Trinity)
3. **Work Distribution** → How to split computation
4. **Queues & Buffers** → Absorbing variation
5. **Retries & Timeouts** → Handling failures gracefully
6. **Case Study 1** → E-commerce platform architecture
7. **[PRACTITIONER]** → Ready for real systems

### Exercises Along the Way:
- 🔧 Calculate latency budgets for your region
- 🔧 Build a simple failure detector
- 🔧 Design a basic work queue

## Senior IC Line 🔵

**Journey Time**: 15-20 hours  
**Destination**: Distributed systems architect

### Your Stops:
1. **[START]** → Axiom speed run (you know basics)
2. **All 8 Axioms** → Complete theoretical foundation
3. **All 5 Pillars** → Work, State, Truth, Control, Intelligence
4. **Patterns 45-64** → Advanced patterns (CRDTs, Sagas, etc.)
5. **Quantitative Tools** → Capacity planning, cost modeling
6. **Case Studies** → All complex multi-region systems
7. **[ARCHITECT]** → Design planet-scale systems

### Exercises Along the Way:
- 🔧 Derive CAP theorem from axioms
- 🔧 Build a consistency decision tree
- 🔧 Design a geo-distributed system

## Engineering Manager Line 🟠

**Journey Time**: 10-15 hours  
**Destination**: Technical leader who makes informed trade-offs

### Your Stops:
1. **[START]** → Executive summary of axioms
2. **Axioms 1,3,7,8** → Latency, Failure, Human, Economics
3. **Pillars Overview** → 20% that gives 80% understanding
4. **Human Factors** → Cognitive load, operational burden
5. **Organizational Physics** → Conway's Law in practice
6. **Case Studies** → Focus on failures and recovery
7. **[LEADER]** → Guide teams through trade-offs

### Exercises Along the Way:
- 🔧 Review your runbooks against axioms
- 🔧 Calculate true cost of your architecture
- 🔧 Design an incident response flow

## Express Route 🔴

**Journey Time**: 1-2 hours  
**Destination**: Immediate solution to specific problem

### Your Stops:
1. **[URGENT]** → What's on fire?
2. **Spider Chart** → Quick pattern match
3. **Decision Tree** → Find your branch
4. **Relevant Pattern** → Deep dive on solution
5. **Worked Example** → See it in practice
6. **[SOLUTION]** → Apply to your system

### Common Express Scenarios:
- "Should I use 2PC or Saga?" → Page 67
- "How many replicas do I need?" → Page 34
- "Why is my system slow?" → Page 12
- "Event sourcing vs state-based?" → Page 78

## Icon Legend

Throughout your journey, watch for these symbols:

- 🎯 **Decision Point**: Major architectural choice ahead
- ⚠️ **Common Pitfall**: Where systems typically fail
- 💡 **Insight Box**: Counter-intuitive truth revealed
- 🔧 **Try This**: Hands-on exercise (<5 minutes)
- 📊 **Measure This**: Key instrumentation point
- 🎬 **Real Story**: Anonymized failure vignette
- 🧮 **Calculate**: Numerical example
- 🔗 **Cross-Link**: Related concept elsewhere

## Checkpoint System

At each major stop, you'll find:

### Knowledge Check ✓
- 3 questions to verify understanding
- If you can't answer → review section
- If you can answer → proceed confidently

### Application Challenge 🎯
- Real scenario to apply concepts
- Solutions provided with trade-offs
- Multiple valid approaches discussed

## Time Investment Guide

### Have 15 minutes?
- Read one axiom deeply
- Do one "Try This" exercise
- Review one failure story

### Have 1 hour?
- Complete one learning path segment
- Work through one case study
- Build one decision tree

### Have 1 day?
- Complete entire learning path
- Do all exercises for your role
- Design a system using principles

## Navigation Tips

1. **Don't Skip Axioms** - Everything builds on them
2. **Do Try Exercises** - Theory without practice is dangerous
3. **Read Failure Stories** - Learn from others' pain
4. **Use Decision Trees** - Systematic > intuitive
5. **Challenge Everything** - If it's not physics, question it

## Ready to Begin?

Choose your line and board the train:

<div class="start-buttons">
  {{ card(type='feature', title='New Graduate', content='Start with fundamentals', link='/part1-axioms/axiom1-latency/') }}
  {{ card(type='feature', title='Senior IC', content='Dive into all axioms', link='/part1-axioms/') }}
  {{ card(type='feature', title='Manager', content='Focus on trade-offs', link='/part1-axioms/axiom1-latency/summary/') }}
  {{ card(type='feature', title='Express', content='Solve immediate problem', link='/patterns/decision-tree/') }}
</div>

---

*"A journey of a thousand nodes begins with a single axiom"*