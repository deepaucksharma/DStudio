---
title: Reference Materials
description: Your comprehensive reference for distributed systems concepts, terms, and practical guides.
type: reference
difficulty: intermediate
reading_time: 5 min
prerequisites: []
status: complete
completion_percentage: 100
last_updated: 2025-07-20
---

# Reference Materials

<nav aria-label="breadcrumb">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="../index.md">Home</a></li>
    <li class="breadcrumb-item active" aria-current="page">Reference</li>
  </ol>
</nav>

<p class="hero-quote">"Your comprehensive guide to distributed systems knowledge - from fundamental concepts to practical implementation"</p>

## 📚 Quick Navigation

<div class="grid cards" markdown>

- :material-book:{ .lg .middle } **Glossary**
    
    ---
    
    400+ terms defined with comprehensive definitions
    
    [Learn more →](glossary.md)

- :material-clipboard-text:{ .lg .middle } **Cheat Sheets**
    
    ---
    
    Quick reference guides for formulas & decisions
    
    [Learn more →](cheat-sheets.md)

- :material-chef-hat:{ .lg .middle } **Recipe Cards**
    
    ---
    
    Step-by-step guides for implementation patterns
    
    [Learn more →](recipe-cards.md)

- :material-lock:{ .lg .middle } **Security Guide**
    
    ---
    
    Security patterns, vulnerabilities & defenses
    
    [Learn more →](security.md)

- :material-map:{ .lg .middle } **Law Mapping**
    
    ---
    
    Framework evolution and 7-law structure guide
    
    [Learn more →](law-mapping-guide.md)

</div>

## Reference by Category

### [Glossary](glossary.md)
Definitions of all distributed systems terms. From "Law" to "Vector Clock". Updated for the 7-law framework.

### [Cheat Sheets](cheat-sheets.md)
Quick reference for calculations, decisions, and pattern selection. Aligned with the 7 fundamental laws.

### [Recipe Cards](recipe-cards.md)
Step-by-step procedures for implementing patterns and debugging. Cross-referenced with relevant laws.

### [Security Considerations](security.md)
Security implications, vulnerabilities, and defensive strategies. Mapped to the fundamental laws.

### [Law Mapping Guide](law-mapping-guide.md)
Complete mapping between old 8-law structure and new 7-law framework 🗺️.

---

## Quick Access

### Fundamental Concepts
<div class="term-category">
 <h4>Consistency Models</h4>
 <ul>
 <li><a href="glossary.md#cap-theorem">CAP Theorem</a></li>
 <li><a href="glossary.md#pacelc-theorem">PACELC Theorem</a></li>
 <li><a href="glossary.md#base-principles">BASE Principles</a></li>
 <li><a href="glossary.md#linearizability">Linearizability</a></li>
 <li><a href="glossary.md#sequential-consistency">Sequential Consistency</a></li>
 <li><a href="glossary.md#eventual-consistency">Eventual Consistency</a></li>
 </ul>
 
 <h4>Time & Ordering</h4>
 <ul>
 <li><a href="glossary.md#vector-clock">Vector Clocks</a></li>
 <li><a href="glossary.md#lamport-timestamp">Lamport Timestamps</a></li>
 <li><a href="glossary.md#hybrid-logical-clock">Hybrid Logical Clocks</a></li>
 <li><a href="glossary.md#happens-before">Happens-Before Relation</a></li>
 <li><a href="glossary.md#causality">Causality</a></li>
 </ul>
 
 <h4>Failure Types</h4>
 <ul>
 <li><a href="glossary.md#byzantine-failure">Byzantine Failures</a></li>
 <li><a href="glossary.md#metastable-failure">Metastable Failures</a></li>
 <li><a href="glossary.md#gray-failure">Gray Failures</a></li>
 <li><a href="glossary.md#cascading-failure">Cascading Failures</a></li>
 <li><a href="glossary.md#correlated-failure">Correlated Failures</a></li>
 </ul>
 
 <h4>Key Patterns</h4>
 <ul>
 <li><a href="../pattern-library/circuit-breaker.md">Circuit Breaker</a></li>
 <li><a href="../pattern-library/saga.md">Saga Pattern</a></li>
 <li><a href="../pattern-library/event-sourcing.md">Event Sourcing</a></li>
 <li><a href="../pattern-library/cqrs.md">CQRS</a></li>
 <li><a href="../pattern-library/consensus.md">Consensus Protocols</a></li>
 </ul>
</div>

### 🧮 Essential Calculations
<table class="responsive-table">
 <thead>
 <tr>
 <th>Formula</th>
 <th>Description</th>
 <th>When to Use</th>
 </tr>
 </thead>
 <tbody>
 <tr>
 <td data-label="Formula"><a href="cheat-sheets.md#littles-law">Little's Law</a></td>
 <td data-label="Description">L = λW (Queue length = Arrival rate × Wait time)</td>
 <td data-label="When to Use">Capacity planning, queue analysis</td>
 </tr>
 <tr>
 <td data-label="Formula"><a href="cheat-sheets.md#availability-math">Availability</a></td>
 <td data-label="Description">A = MTTF / (MTTF + MTTR)</td>
 <td data-label="When to Use">SLA calculations, redundancy planning</td>
 </tr>
 <tr>
 <td data-label="Formula"><a href="cheat-sheets.md#amdahls-law">Amdahl's Law</a></td>
 <td data-label="Description">S = 1 / (s + p/n)</td>
 <td data-label="When to Use">Parallelization limits</td>
 </tr>
 <tr>
 <td data-label="Formula"><a href="cheat-sheets.md#universal-scalability">USL</a></td>
 <td data-label="Description">C(N) = N / (1 + α(N-1) + βN(N-1))</td>
 <td data-label="When to Use">Scalability modeling</td>
 </tr>
 <tr>
 <td data-label="Formula"><a href="../quantitative/queueing-models.md">M/M/1 Queue</a></td>
 <td data-label="Description">W = 1 / (μ - λ)</td>
 <td data-label="When to Use">Service time estimation</td>
 </tr>
 </tbody>
 </table>

### 🛠 Common Procedures
<div class="procedure-category">
 <h4>Implementation Guides</h4>
 <ul>
 <li><a href="recipe-cards.md#recipe-implementing-circuit-breaker">Implementing Circuit Breaker</a></li>
 <li><a href="recipe-cards.md#recipe-implementing-rate-limiter">Building Rate Limiter</a></li>
 <li><a href="recipe-cards.md#recipe-distributed-tracing">Setting Up Distributed Tracing</a></li>
 <li><a href="recipe-cards.md#recipe-implementing-saga">Implementing Saga Pattern</a></li>
 </ul>
 
 <h4>Debugging & Troubleshooting</h4>
 <ul>
 <li><a href="recipe-cards.md#recipe-debugging-distributed-failures">Debugging Distributed Failures</a></li>
 <li><a href="recipe-cards.md#recipe-performance-investigation">Performance Investigation</a></li>
 <li><a href="recipe-cards.md#recipe-troubleshooting-cascading-failures">Handling Cascading Failures</a></li>
 <li><a href="recipe-cards.md#recipe-debugging-consistency-issues">Debugging Consistency Issues</a></li>
 </ul>
 
 <h4>Operations & Monitoring</h4>
 <ul>
 <li><a href="recipe-cards.md#recipe-essential-observability-stack">Essential Observability Stack</a></li>
 <li><a href="recipe-cards.md#recipe-monitoring-setup">Monitoring Setup Guide</a></li>
 <li><a href="recipe-cards.md#recipe-incident-response">Incident Response Process</a></li>
 <li><a href="recipe-cards.md#recipe-chaos-engineering">Chaos Engineering Setup</a></li>
 </ul>
 
 <h4>Planning & Design</h4>
 <ul>
 <li><a href="recipe-cards.md#recipe-capacity-planning">Capacity Planning Process</a></li>
 <li><a href="recipe-cards.md#recipe-architecture-review">Architecture Review Checklist</a></li>
 <li><a href="recipe-cards.md#recipe-migration-planning">Migration Planning Guide</a></li>
 <li><a href="recipe-cards.md#recipe-disaster-recovery">Disaster Recovery Planning</a></li>
 </ul>
</div>

## Quick Decision Trees

!!! note "🤔 Which Consistency Model?"
 <ul>
 <li>Need global ordering? → <strong>Linearizability</strong></li>
 <li>Can tolerate stale reads? → <strong>Eventual Consistency</strong></li>
 <li>Need causal relationships? → <strong>Causal Consistency</strong></li>
 <li>Session guarantees enough? → <strong>Session Consistency</strong></li>
 </ul>
 <a href="cheat-sheets.md#consistency-model-selection">Full decision tree →</a>
 
 !!! note "🔧 Which Pattern to Use?"
 <ul>
 <li>Handling failures? → <strong>Circuit Breaker</strong></li>
 <li>Distributed transactions? → <strong>Saga Pattern</strong></li>
 <li>Event history needed? → <strong>Event Sourcing</strong></li>
 <li>Read/write separation? → <strong>CQRS</strong></li>
 </ul>
 <a href="cheat-sheets.md#pattern-selection-guide">Full pattern selector →</a>

## 📖 How to Use These References

<div class="user-type">
 <h4>👨‍🎓 For Students</h4>
 <ol>
 <li>Start with <strong>Glossary</strong> for definitions</li>
 <li>Use <strong>Cheat Sheets</strong> during study</li>
 <li>Practice with <strong>Recipe Cards</strong></li>
 <li>Review <strong>Security</strong> considerations</li>
 </ol>
 
 <h4>👩‍💼 For Practitioners</h4>
 <ol>
 <li>Quick lookups in <strong>Glossary</strong></li>
 <li>Decision support in <strong>Cheat Sheets</strong></li>
 <li>Implementation via <strong>Recipe Cards</strong></li>
 <li>Security review with <strong>Security Guide</strong></li>
 </ol>
 
 <h4>🎤 For Interviews</h4>
 <ol>
 <li>Review key terms in <strong>Glossary</strong></li>
 <li>Memorize formulas from <strong>Cheat Sheets</strong></li>
 <li>Practice explanations with <strong>Recipe Cards</strong></li>
 <li>Understand trade-offs via <strong>Law Mapping</strong></li>
 </ol>
</div>

## Pro Tips

<div class="tip-card">
 <span class="tip-icon">🔖</span>
 <p>Bookmark frequently used sections for quick access during incidents</p>
 <span class="tip-icon">🖨️</span>
 <p>Print cheat sheets and keep them at your desk for rapid reference</p>
 <span class="tip-icon">📝</span>
 <p>Create personal notes linking concepts to your system's specifics</p>
 <span class="tip-icon">🔄</span>
 <p>Review glossary monthly to reinforce terminology and concepts</p>
</div>

---

## Navigation

<div class="navigation-footer">
    <div class="navigation-prev">
        ← [Human Factors](../human-factors/index.md)
    </div>
    <div class="navigation-next">
        [Glossary](glossary.md) →
    </div>
</div>

