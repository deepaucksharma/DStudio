# The Compendium of Distributed Systems

<div class="hero-container">
  <div class="hero-animation">
    <canvas id="network-visualization"></canvas>
  </div>
  <div class="hero-content">
    <h1 class="hero-title">Master Distributed Systems from <span class="highlight">First Principles</span></h1>
    <p class="hero-subtitle">Derive patterns from physics, not memorization</p>
    <div class="hero-stats">
      <div class="stat-item">
        <span class="stat-number">8</span>
        <span class="stat-label">Fundamental Axioms</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">6</span>
        <span class="stat-label">Core Pillars</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">50+</span>
        <span class="stat-label">Real-World Cases</span>
      </div>
    </div>
    <div class="hero-cta">
      <a href="introduction/" class="hero-button primary">Begin Your Journey</a>
      <a href="#interactive-journey-map" class="hero-button secondary">Explore Concepts</a>
    </div>
    <a href="#interactive-journey-map" class="scroll-hint">
      <span class="scroll-text">↓ Journey Map</span>
    </a>
  </div>
</div>

---

## 🚀 Quick Navigation

<div class="grid cards" markdown>

- :material-map:{ .lg .middle } **[Learning Paths →](introduction/roadmap.md)**

    ---

    Choose a customized path based on your role and experience level

- :material-lightbulb:{ .lg .middle } **[Key Concepts →](#what-youll-learn)**

    ---

    Explore the 8 fundamental axioms that govern all distributed systems

- :material-github:{ .lg .middle } **[Contribute →](https://github.com/deepaucksharma/DStudio)**

    ---

    Join our community and help improve this resource

</div>

## 🗺️ Interactive Journey Map {#interactive-journey-map}

<div id="journey-map-container">
    <div class="journey-legend">
        <div class="legend-item">
            <span class="legend-dot axiom"></span>
            <span>Core Axiom</span>
        </div>
        <div class="legend-item">
            <span class="legend-dot pillar"></span>
            <span>Foundational Pillar</span>
        </div>
        <div class="legend-item">
            <span class="legend-dot tool"></span>
            <span>Interactive Tool</span>
        </div>
    </div>
    
    <div id="journey-map" class="journey-map">
        <!-- SVG will be injected here by JavaScript -->
    </div>
    
    <div class="journey-details" id="journey-details">
        <h3>Click any node to explore</h3>
        <p>Navigate through axioms, pillars, and tools to build your understanding.</p>
    </div>
</div>


## 🎯 Our Philosophy

This project takes a unique approach to teaching distributed systems:

- **Physics First**: We start with the speed of light, not with Kafka
- **Math Over Mythology**: Quantitative trade-offs replace "best practices"
- **Failures as Teachers**: Real production disasters illuminate principles
- **Derive, Don't Memorize**: Every pattern emerges from fundamental constraints


## 📚 What You'll Learn

<div class="axiom-box animate-fadeIn">

### The Eight Fundamental Axioms

<div class="axiom-grid">

<div class="axiom-item">
<h4 class="axiom-item__icon">⚡</h4>
<div class="axiom-item__title">Latency</div>
<p class="axiom-item__description">Speed of light is non-negotiable</p>
</div>

<div class="axiom-item">
<h4 class="axiom-item__icon">📦</h4>
<div class="axiom-item__title">Finite Capacity</div>
<p class="axiom-item__description">Every resource has a breaking point</p>
</div>

<div class="axiom-item">
<h4 class="axiom-item__icon">💥</h4>
<div class="axiom-item__title">Failure</div>
<p class="axiom-item__description">Components will fail; plan accordingly</p>
</div>

<div class="axiom-item">
<h4 class="axiom-item__icon">⚖️</h4>
<div class="axiom-item__title">Consistency</div>
<p class="axiom-item__description">You can't have your cake and eat it too</p>
</div>

<div class="axiom-item">
<h4 class="axiom-item__icon">⏰</h4>
<div class="axiom-item__title">Time</div>
<p class="axiom-item__description">There is no "now" in distributed systems</p>
</div>

<div class="axiom-item">
<h4 class="axiom-item__icon">🔄</h4>
<div class="axiom-item__title">Ordering</div>
<p class="axiom-item__description">Events happen, but in what order?</p>
</div>

<div class="axiom-item">
<h4 class="axiom-item__icon">🧩</h4>
<div class="axiom-item__title">Knowledge</div>
<p class="axiom-item__description">Partial information is the only information</p>
</div>

<div class="axiom-item">
<h4 class="axiom-item__icon">📈</h4>
<div class="axiom-item__title">Growth</div>
<p class="axiom-item__description">Systems evolve or die</p>
</div>

</div>

</div>

## 🛠️ Key Features

- **🎬 Real Failure Stories**: Learn from anonymized production disasters
- **🧮 Quantitative Tools**: Make decisions with math, not gut feelings
- **🔧 Hands-On Exercises**: Try concepts in under 5 minutes
- **💡 Counter-Intuitive Truths**: Challenge your assumptions
- **🎯 Decision Frameworks**: Know when to use which pattern

## 🌟 Why This Approach?

| Traditional Learning | Our Approach |
|---------------------|--------------|
| Memorize patterns | Derive patterns from physics |
| "Best practices" | Context-dependent trade-offs |
| Tool-specific knowledge | Timeless principles |
| Academic theory OR practice | Theory THROUGH practice |

## 🚦 Quick Start: Your First Insight

<div class="truth-box">

### Why does adding more servers sometimes make your system slower?

<div class="grid grid--2">

<div>
<h4>📊 The Math</h4>

- 2 servers = 1 connection
- 5 servers = 10 connections  
- 10 servers = 45 connections
- n servers = n(n-1)/2 connections

**Coordination cost**: O(n²)  
**Capacity growth**: O(n)
</div>

<div>
<h4>💡 The Lesson</h4>

Sometimes the best distributed system is the one that isn't distributed. Before adding complexity:

1. **Optimize** what you have
2. **Measure** actual bottlenecks
3. **Calculate** coordination overhead
4. **Consider** vertical scaling first
</div>

</div>

</div>


---

<div class="text-center my-6">
    <a href="introduction/index.md" class="btn btn--primary btn--lg">
        Begin Your Journey →
    </a>
</div>

<div class="text-center text-neutral-600 text-sm mt-6">
    Built with ❤️ using <a href="https://squidfunk.github.io/mkdocs-material/">Material for MkDocs</a>
</div>

