# Pillar 5: Distribution of Intelligence

<div class="pillar-header">
  <div class="learning-objective">
    <strong>Learning Objective</strong>: Master building systems that learn, adapt, and improve themselves while operating within economic constraints.
  </div>
</div>

---

## Level 1: Intuition (Start Here) 🌱

### The Thermostat Evolution Metaphor

Think about temperature control evolution:
- **Manual**: You adjust heat when cold
- **Basic Thermostat**: Maintains set temperature
- **Smart Thermostat**: Learns your schedule
- **Intelligent Home**: Predicts needs, saves energy
- **Adaptive System**: Optimizes comfort vs cost

**This is distributed intelligence**: Systems that learn from experience and improve autonomously.

### Real-World Analogy: Restaurant Kitchen Intelligence

```
Evolution of a Restaurant Kitchen:

Week 1: Manual Everything
- Chef tastes every dish
- Writes down popular items
- Adjusts portions by memory

Month 1: Basic Patterns
- Track bestsellers
- Standard portion sizes
- Rush hour prep lists

Year 1: Smart Operations
- Predict busy nights
- Dynamic menu pricing
- Inventory optimization
- Staff scheduling AI

Intelligence emerges from:
- Data (orders, feedback)
- Patterns (busy times)
- Adaptation (menu changes)
- Feedback loops (reviews)
```

### Your First Intelligence Experiment

<div class="experiment-box">
<h4>🧪 The Learning Game</h4>

Play this pattern recognition game:

**Round 1: Manual Rules**
- Write rules for sorting emails
- If sender = boss, then important
- Gets complex fast!
- Many edge cases

**Round 2: Learning from Examples**
- Show system 100 sorted emails
- It learns patterns
- Handles new cases better
- Improves with feedback

**Round 3: Adaptive Intelligence**
- System updates continuously
- Learns your changing preferences
- Suggests new categories
- Gets smarter over time

**Lesson**: Intelligence emerges from data + feedback
</div>

### The Beginner's Intelligence Stack

```
         🧠 Human Intelligence
          (Strategic decisions)
                |
                |
         🤖 Augmented Intelligence
           (AI assists humans)
                |
                |
         📊 Automated Intelligence
           (Rule-based systems)
                |
                |
         🔄 Adaptive Intelligence
           (Learning systems)
```

---

## 📋 Questions This Pillar Answers

<div class="questions-box">

### Fundamental Questions
- **How do I make my system learn from its operations?**
- **What patterns should my system detect automatically?**
- **When is ML/AI worth the complexity?**
- **How do I prevent learning systems from going wrong?**

### Design Questions
- **Where should intelligence live in my architecture?**
- **How do I balance reactive vs predictive behavior?**
- **Should I use centralized or federated learning?**
- **How do I design effective feedback loops?**

### Operational Questions
- **How do I debug learned behaviors?**
- **When should I override automated decisions?**
- **How do I detect model drift in production?**
- **What metrics show if intelligence is helping?**

### Performance Questions
- **What's the latency cost of intelligent decisions?**
- **How do I scale inference across regions?**
- **When does caching predictions make sense?**
- **How do I measure the ROI of intelligence features?**

</div>

---

## Level 2: Foundation (Understand Why) 🌿

### Core Principle: Intelligence Emerges from Feedback

<div class="principle-box">
<h3>The Fundamental Intelligence Theorem</h3>

```
Intelligence = Data + Algorithms + Feedback Loops

Where:
- Data = Observations of the world
- Algorithms = Ways to find patterns
- Feedback = Learning from outcomes
```

**Example**: Recommendation Systems
- Netflix watches what you watch (Data)
- Finds patterns in viewing habits (Algorithms)
- Improves when you watch/skip (Feedback)
- Result: 80% of views from recommendations
</div>

### The Intelligence Spectrum

<div class="intelligence-types">
<h3>🎯 Types of System Intelligence</h3>

```
1. Reactive Intelligence (Immediate)
   Input → Rules → Output
   Example: Spam filter
   No memory, just patterns

2. Limited Memory (Short-term)
   Recent inputs → Model → Output
   Example: Traffic prediction
   Uses recent history

3. Theory of Mind (Understanding)
   Context → Reasoning → Output
   Example: Customer service bot
   Understands intent

4. Self-Aware (Adaptive)
   Self-monitoring → Learning → Evolution
   Example: Self-optimizing database
   Improves autonomously
```
</div>

### The Learning Hierarchy

```
Supervised Learning 📚
├─ Learn from labeled examples
├─ "This email is spam"
├─ Predict labels for new data
└─ Use case: Classification

Unsupervised Learning 🔍
├─ Find patterns without labels
├─ "These users are similar"
├─ Discover hidden structure
└─ Use case: Clustering

Reinforcement Learning 🎮
├─ Learn from rewards/penalties
├─ "That action increased revenue"
├─ Optimize future actions
└─ Use case: Decision making

Transfer Learning 🔄
├─ Apply knowledge across domains
├─ "Image recognition → Medical imaging"
├─ Leverage existing models
└─ Use case: Limited data scenarios
```

### 🎬 Failure Vignette: The Flash Crash of 2010

<div class="failure-story">
<h3>When Intelligent Systems Spiral</h3>

**Date**: May 6, 2010, 2:45 PM
**Event**: Dow Jones drops 1000 points in minutes
**Cause**: Intelligent trading algorithms

**The Cascade**:
```
2:32 PM: Large sell order enters market
2:41 PM: HFT algorithms detect anomaly
2:42 PM: Algorithms start rapid selling
2:43 PM: Other algorithms detect selling
2:44 PM: Feedback loop amplifies
2:45 PM: Market drops 9% in 5 minutes
2:47 PM: Circuit breakers trigger
3:07 PM: Market partially recovers

Total impact: $1 trillion temporary loss
```

**What Happened**:
1. Algorithms optimized for speed
2. No understanding of context
3. Positive feedback loops
4. Herd behavior in algorithms
5. Intelligence without wisdom

**Lesson**: Intelligence needs guardrails
**Fix**: Circuit breakers and human oversight
</div>

### Building Blocks of Intelligence

<div class="ml-components">
<h3>🔧 Core ML Components</h3>

| Component | Purpose | Example |
|-----------|---------|---------|
| **Feature Engineering** | Extract meaningful signals | User age → Age group |
| **Model Selection** | Choose right algorithm | Linear vs Neural Network |
| **Training Process** | Learn from data | Gradient descent |
| **Evaluation Metrics** | Measure success | Accuracy, Precision |
| **Deployment Pipeline** | Productionize models | A/B testing framework |
</div>

### Concept Map: Distribution of Intelligence

```mermaid
graph TB
    subgraph "Intelligence Distribution Pillar"
        Core[Distribution of Intelligence<br/>Core Concept]
        
        Core --> Learning[Learning<br/>Paradigms]
        Core --> Architecture[Intelligence<br/>Architecture]
        Core --> Feedback[Feedback<br/>Loops]
        Core --> Governance[Intelligence<br/>Governance]
        
        %% Learning branch
        Learning --> Supervised[Supervised<br/>Labeled data]
        Learning --> Unsupervised[Unsupervised<br/>Pattern finding]
        Learning --> Reinforcement[Reinforcement<br/>Reward-based]
        Learning --> Federated[Federated<br/>Privacy-preserving]
        
        %% Architecture branch
        Architecture --> Centralized[Centralized ML<br/>Single model]
        Architecture --> Edge[Edge Intelligence<br/>Local inference]
        Architecture --> Hybrid[Hybrid<br/>Edge + Cloud]
        Architecture --> Swarm[Swarm Intelligence<br/>Emergent behavior]
        
        %% Feedback branch
        Feedback --> Implicit[Implicit Feedback<br/>User behavior]
        Feedback --> Explicit[Explicit Feedback<br/>Ratings/Labels]
        Feedback --> Continuous[Continuous Learning<br/>Online updates]
        Feedback --> Batch[Batch Learning<br/>Periodic retraining]
        
        %% Governance branch
        Governance --> Explainability[Explainability<br/>Why decisions?]
        Governance --> Fairness[Fairness<br/>Bias detection]
        Governance --> Privacy[Privacy<br/>Data protection]
        Governance --> Safety[Safety<br/>Bounded behavior]
        
        %% Key relationships
        Federated -.-> Privacy
        Edge -.-> Continuous
        Reinforcement -.-> Safety
        Swarm -.-> Unsupervised
        
        %% Axiom connections
        Axiom1[Axiom 1: Latency] --> Edge
        Axiom2[Axiom 2: Capacity] --> Architecture
        Axiom6[Axiom 6: Observability] --> Explainability
        Axiom7[Axiom 7: Human Interface] --> Governance
        Axiom8[Axiom 8: Economics] --> Feedback
    end
    
    style Core fill:#f9f,stroke:#333,stroke-width:4px
    style Axiom1 fill:#e1e1ff,stroke:#333,stroke-width:2px
    style Axiom2 fill:#e1e1ff,stroke:#333,stroke-width:2px
    style Axiom6 fill:#e1e1ff,stroke:#333,stroke-width:2px
    style Axiom7 fill:#e1e1ff,stroke:#333,stroke-width:2px
    style Axiom8 fill:#e1e1ff,stroke:#333,stroke-width:2px
```

This concept map shows how distributed intelligence encompasses learning paradigms, architectural choices, feedback mechanisms, and governance requirements. Each aspect must balance performance, privacy, and practical constraints.

---

## Level 3: Deep Dive (Master the Patterns) 🌳

### Multi-Armed Bandits: Exploration vs Exploitation

<div class="bandit-explanation">
<h3>🎰 The Restaurant Menu Problem</h3>

**Scenario**: Which dish to recommend?
```
The Dilemma:
- Recommend popular dishes (exploit)
- Try new dishes (explore)
- Balance is crucial

Thompson Sampling Solution:
1. Track success rate for each dish
2. Model uncertainty with Beta distribution
3. Sample from distributions
4. Recommend highest sample
5. Update based on feedback

Math intuition:
- More data → Less uncertainty
- New items → High uncertainty
- Algorithm naturally explores uncertain options
```

**Real Implementation**:
```
For each recommendation:
1. Calculate success probability + uncertainty
2. Add controlled randomness
3. Track user response
4. Update probability estimates
5. Gradually converge on best options
```
</div>

### Online Learning Systems

<div class="online-learning">
<h3>📈 Learning from Streams</h3>

**Challenge**: Learn from continuous data
```
Traditional: Batch Learning
├─ Collect all data
├─ Train model once
├─ Deploy static model
└─ Retrain periodically

Modern: Online Learning
├─ Process each data point
├─ Update model incrementally
├─ Adapt to changes quickly
└─ No full retraining needed
```

**Example: Fraud Detection**
```
Stream Processing:
Transaction → Feature Extraction → Score → Decision
     ↓                                        ↓
  Update Model ← ← ← Feedback ← ← ← ← ← Result

Benefits:
- Adapts to new fraud patterns
- No downtime for retraining
- Handles concept drift
- Memory efficient
```
</div>

### Recommendation Systems Architecture

<div class="recommendation-architecture">
<h3>🎯 Modern Recommendation Pipeline</h3>

```
1. Candidate Generation (Recall)
   ├─ Collaborative filtering
   ├─ Content similarity
   ├─ Trending items
   └─ Output: 1000s of candidates

2. Feature Extraction
   ├─ User features (history, demographics)
   ├─ Item features (category, popularity)
   ├─ Context features (time, device)
   └─ Cross features (user-item interaction)

3. Ranking (Precision)
   ├─ Deep neural network
   ├─ Predict engagement probability
   ├─ Consider multiple objectives
   └─ Output: Ranked list

4. Business Logic
   ├─ Diversity injection
   ├─ Freshness boost
   ├─ Creator fairness
   └─ Final reranking

5. Serving
   ├─ Real-time inference
   ├─ Caching strategies
   ├─ Fallback logic
   └─ A/B testing
```
</div>

### Anomaly Detection Patterns

<div class="anomaly-detection">
<h3>🚨 Finding Needles in Haystacks</h3>

**Statistical Methods**:
```
Z-Score Method:
- Calculate mean and standard deviation
- Flag points > 3 standard deviations
- Simple but assumes normal distribution

Isolation Forest:
- Randomly partition data
- Anomalies isolated quickly
- Works for any distribution
- No training labels needed
```

**Machine Learning Methods**:
```
Autoencoder Approach:
1. Train to reconstruct normal data
2. High reconstruction error = anomaly
3. Learns complex normal patterns
4. Adapts to data changes

One-Class SVM:
1. Learn boundary of normal data
2. Points outside = anomalies
3. Works in high dimensions
4. Robust to outliers
```

**Ensemble Methods**:
```
Combine multiple detectors:
├─ Statistical baseline
├─ ML model predictions
├─ Rule-based checks
└─ Vote or weighted average
```
</div>

### Intelligence System Decision Framework

<div class="decision-framework">
<h4>🎯 When to Add Intelligence</h4>

| Problem Type | Use ML/AI | Use Rules | Use Heuristics | Why |
|--------------|-----------|-----------|----------------|-----|
| **Pattern Recognition** | ✅ Complex patterns | ❌ Too rigid | ⚠️ Simple patterns | ML excels at finding hidden patterns |
| **Personalization** | ✅ Individual level | ⚠️ Segments only | ❌ Too generic | ML scales to millions of users |
| **Anomaly Detection** | ✅ Unknown unknowns | ⚠️ Known patterns | ❌ Too many false positives | ML adapts to new anomalies |
| **Optimization** | ✅ Multi-objective | ⚠️ Single metric | ✅ Good enough | ML handles complex trade-offs |
| **Forecasting** | ✅ Complex seasonality | ⚠️ Simple trends | ✅ Short-term only | ML captures non-linear patterns |

<h4>🔧 Intelligence Architecture Patterns</h4>

| Pattern | Use When | Avoid When | Example |
|---------|----------|------------|---------|
| **Online Learning** | • Concept drift<br>• Real-time adaptation<br>• Continuous improvement | • Stable patterns<br>• Need explainability<br>• Limited compute | Fraud detection |
| **Federated Learning** | • Privacy critical<br>• Edge devices<br>• Data sovereignty | • Need central data<br>• Simple models<br>• Real-time updates | Mobile keyboards |
| **Ensemble Models** | • High accuracy needed<br>• Reduce variance<br>• Different perspectives | • Latency sensitive<br>• Resource constrained<br>• Need interpretability | Risk scoring |
| **Transfer Learning** | • Limited training data<br>• Similar domains<br>• Quick deployment | • Unique problem<br>• Abundant data<br>• Domain mismatch | Image classification |
| **Reinforcement Learning** | • Sequential decisions<br>• Clear rewards<br>• Can simulate | • One-shot decisions<br>• Unclear objectives<br>• Safety critical | Game AI, routing |

<h4>🚨 Intelligence Anti-Patterns</h4>

| Anti-Pattern | Signs | Better Approach |
|--------------|-------|-----------------|
| **ML for Everything** | • Simple if-then suffices<br>• No data to train<br>• Interpretability required | Start with rules, add ML where needed |
| **Black Box Production** | • Can't explain decisions<br>• No debugging ability<br>• Regulatory issues | Use interpretable models or LIME/SHAP |
| **Accuracy Obsession** | • 99% → 99.1% at 10x cost<br>• Ignoring latency<br>• Model too complex | Consider business value vs cost |
| **Static Models** | • Performance degrading<br>• World has changed<br>• No monitoring | Implement drift detection and retraining |
| **Data Leakage** | • Too-good-to-be-true results<br>• Fails in production<br>• Future data in training | Strict train/test splits, temporal validation |

</div>

### A/B Testing at Scale

<div class="ab-testing">
<h3>🔬 Experimentation Framework</h3>

**Multi-Armed Bandit A/B Testing**:
```
Traditional A/B:
- Fixed split (50/50)
- Run for fixed time
- Wastes traffic on losing variant

Bandit Approach:
- Dynamic allocation
- More traffic to winner
- Continuous optimization
- Handles multiple variants

Implementation:
1. Start with equal allocation
2. Measure conversion rates
3. Shift traffic to winners
4. Maintain exploration budget
5. Statistical significance checks
```

**Challenges at Scale**:
```
Network Effects:
- User interactions affect each other
- Can't assume independence
- Need cluster randomization

Multiple Experiments:
- Feature interactions
- Statistical pollution
- Need isolation strategies

Long-term Effects:
- Novelty effects wear off
- User learning changes behavior
- Need holdout groups
```
</div>

---

## Level 4: Expert (Production Patterns) 🌲

### Case Study: Netflix Recommendation Evolution

<div class="case-study">
<h3>🎬 From Ratings to Deep Learning</h3>

**Timeline of Intelligence Evolution**:
```
2006: Cinematch (Collaborative Filtering)
- User ratings matrix
- Pearson correlation
- 60% accuracy

2009: Netflix Prize Winner
- Ensemble of 107 algorithms
- Matrix factorization
- 75% accuracy
- Too complex for production

2012: Personalized Rankings
- Beyond star ratings
- Viewing time signals
- Context awareness
- 80% accuracy

2016: Deep Learning Era
- Neural networks
- Rich feature extraction
- Real-time personalization
- 85% accuracy

2020: Causal Inference
- Why users watch
- Counterfactual reasoning
- Long-term optimization
- Business metric focus
```

**Key Insights**:
```
Data Evolution:
Ratings → Views → Engagement → Context

Algorithm Evolution:
Correlation → Factorization → Deep Learning → Causal ML

Metric Evolution:
Accuracy → Engagement → Retention → Revenue

Architecture Evolution:
Batch → Near-real-time → Streaming → Edge
```

**Current Architecture**:
- 100M+ users globally
- 1000+ microservices
- PB-scale data processing
- Sub-100ms recommendations
- Continuous experimentation
</div>

### 🎯 Decision Framework: ML Strategy

<div class="decision-framework">
<h3>🎯 Choosing Intelligence Approaches</h3>

```
1. What's your data situation?
├─ Lots of labeled data? → Supervised learning
│   Example: Email classification
├─ No labels? → Unsupervised learning
│   Example: Customer segmentation
├─ Can simulate? → Reinforcement learning
│   Example: Game AI
└─ Limited data? → Transfer learning
    Example: Medical imaging

2. What's your latency requirement?
├─ Real-time (<10ms)? → Cached predictions
│   Use: Search ranking
├─ Near-time (<100ms)? → Optimized models
│   Use: Recommendations
├─ Batch OK? → Complex models
│   Use: Fraud analysis
└─ Edge device? → Compressed models
    Use: Mobile apps

3. What's your interpretability need?
├─ High stakes? → Linear models, trees
│   Use: Credit decisions
├─ Need explanations? → LIME, SHAP
│   Use: Healthcare
├─ Performance critical? → Deep learning
│   Use: Image recognition
└─ Debugging important? → Simple models
    Use: Early iterations

4. What's your operational maturity?
├─ Starting out? → Simple rules
├─ Growing? → Classical ML
├─ Scaling? → Deep learning
└─ Mature? → AutoML + Human oversight
```
</div>

### Advanced Pattern: Federated Learning

<div class="federated-learning">
<h3>🌐 Privacy-Preserving Intelligence</h3>

**Traditional vs Federated**:
```
Traditional ML:
- Centralize all data
- Train in datacenter
- Privacy concerns
- Bandwidth intensive

Federated Learning:
- Data stays on device
- Send model updates only
- Privacy preserved
- Bandwidth efficient
```

**Implementation Strategy**:
```
1. Server Initialization:
   - Create global model
   - Define aggregation strategy
   - Set privacy budget

2. Client Training:
   - Download global model
   - Train on local data
   - Compute model update
   - Add privacy noise

3. Secure Aggregation:
   - Collect encrypted updates
   - Aggregate without decryption
   - Update global model
   - Broadcast new version

4. Privacy Guarantees:
   - Differential privacy
   - Secure multiparty computation
   - Homomorphic encryption
   - Client sampling
```

**Use Cases**:
- Mobile keyboard predictions
- Healthcare across hospitals
- Financial fraud detection
- IoT sensor networks
</div>

### Production Anti-Patterns

<div class="antipattern-box">
<h3>⚠️ Intelligence Mistakes That Hurt</h3>

**1. The Accuracy Trap**
```
WRONG: Optimize only for accuracy
- 99.9% accuracy finding rare events
- But 99.9% false positive rate!
- Unusable in practice

RIGHT: Optimize for business metrics
- Consider precision vs recall
- Cost of false positives/negatives
- User experience impact
```

**2. The Black Box Production**
```
WRONG: Deploy unexplainable models
- Complex neural network
- No debugging capability
- Can't fix when wrong

RIGHT: Production-ready ML
- Model interpretability
- Feature importance
- Error analysis tools
- Human oversight
```

**3. The Data Leakage Problem**
```
WRONG: Train on future information
- Include target in features
- Time-based leakage
- Overly optimistic metrics

RIGHT: Proper validation
- Time-based splits
- Feature engineering discipline
- Production-like testing
```
</div>

---

## Level 5: Mastery (Push the Boundaries) 🌴

### The Future: Autonomous AI Systems

<div class="future-ai">
<h3>🚀 Self-Improving Intelligence</h3>

**AutoML Evolution**:
```
Generation 1: Hyperparameter Tuning
- Grid search
- Random search
- Bayesian optimization

Generation 2: Architecture Search
- Neural architecture search
- Automated feature engineering
- Transfer learning automation

Generation 3: End-to-End AutoML
- Problem formulation
- Data cleaning
- Model selection
- Deployment automation

Generation 4: Self-Improving Systems
- Continuous learning
- Architecture evolution
- Automated debugging
- Performance optimization
```

**Example: Google's AutoML Zero**
```
Evolution Process:
1. Start with random programs
2. Mutate and crossover
3. Evaluate on tasks
4. Select best performers
5. Repeat for generations

Discoveries:
- Rediscovered backpropagation
- Found novel architectures
- Created new optimizers
- No human ML knowledge needed
```
</div>

### Neuromorphic Computing

<div class="neuromorphic">
<h3>🧠 Brain-Inspired Intelligence</h3>

**Traditional vs Neuromorphic**:
```
Von Neumann Architecture:
- Separate memory/processing
- Sequential execution
- High power consumption
- Good for precise computation

Neuromorphic Architecture:
- Integrated memory/processing
- Massively parallel
- Ultra-low power
- Good for pattern recognition
```

**Spiking Neural Networks**:
```
Traditional NN:
- Continuous activations
- Synchronous updates
- High precision math

Spiking NN:
- Event-based spikes
- Asynchronous updates
- Temporal encoding
- 1000x more efficient
```

**Applications**:
- Real-time sensor processing
- Always-on AI devices
- Brain-computer interfaces
- Autonomous robotics
</div>

### The Philosophy of Intelligence

<div class="philosophy-box">
<h3>🤔 Deep Thoughts on Machine Intelligence</h3>

**Intelligence in Different Domains**:

| Domain | Intelligence Type | Key Principle |
|--------|------------------|---------------|
| **Nature** | Evolutionary | Survival drives adaptation |
| **Markets** | Collective | Price discovery through agents |
| **Brains** | Neural | Parallel pattern processing |
| **Systems** | Emergent | Simple rules, complex behavior |
| **Machines** | Artificial | Optimization through feedback |

**Key Insights**:
1. **Intelligence is substrate-independent**
2. **Learning requires forgetting**
3. **Generalization needs regularization**
4. **Robustness requires diversity**
5. **Adaptation requires exploration**

**The Ultimate Question**:
*"If a system optimizes metrics perfectly but doesn't understand why, is it truly intelligent?"*
</div>

## Summary: Key Insights by Level

### 🌱 Beginner
1. **Intelligence emerges from data + feedback**
2. **Start simple: rules before ML**
3. **Learning systems improve over time**

### 🌿 Intermediate
1. **Different problems need different ML types**
2. **Feature engineering often beats complex models**
3. **Feedback loops can spiral (good or bad)**

### 🌳 Advanced
1. **Exploration/exploitation balance crucial**
2. **Online learning handles changing worlds**
3. **Ensemble methods increase robustness**

### 🌲 Expert
1. **Business metrics > ML metrics**
2. **Federated learning preserves privacy**
3. **Production ML needs interpretability**

### 🌴 Master
1. **AutoML automates ML engineering**
2. **Neuromorphic computing changes efficiency**
3. **True intelligence requires understanding**

## Quick Reference Card

<div class="reference-card">
<h3>📋 Intelligence Patterns Cheat Sheet</h3>

**ML Algorithm Selection**:
```
┌─────────────────────────────────┐
│ Labeled data available?         │
│ ↓ YES              ↓ NO         │
│ Supervised         Unsupervised │
│                                 │
│ Need explanations?              │
│ ↓ YES              ↓ NO         │
│ Trees/Linear       Neural Nets  │
│                                 │
│ Real-time needed?               │
│ ↓ YES              ↓ NO         │
│ Cached/Simple      Complex OK   │
└─────────────────────────────────┘
```

**Learning Approaches**:
```
- Batch: All data at once
- Online: One sample at a time
- Mini-batch: Small groups
- Reinforcement: Learn from rewards
```

**Common Metrics**:
```
Classification:
- Accuracy = Correct / Total
- Precision = True Positives / Predicted Positives
- Recall = True Positives / Actual Positives
- F1 = Harmonic mean of Precision & Recall

Regression:
- MAE = Mean Absolute Error
- RMSE = Root Mean Squared Error
- R² = Explained variance
```

**Production Checklist**:
```
□ Data pipeline robust?
□ Model versioning?
□ A/B testing ready?
□ Monitoring in place?
□ Fallback strategy?
□ Interpretability tools?
```
</div>

---

**Next**: [Tools →](../../tools/index.md)

*"The best AI systems make humans smarter, not obsolete."*