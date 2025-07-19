# The Compendium of Distributed Systems

<div class="hero-section">
  <h2>Learn Distributed Systems from First Principles</h2>
  <p class="hero-quote">"All distributed systems behavior emerges from physical and mathematical constraints"</p>
</div>

## Welcome

This compendium teaches distributed systems from the ground up, starting with fundamental physics and mathematics rather than jumping straight into technologies. We derive patterns from constraints, not fashion.

## Quick Start Paths

{{ grid(columns=4, gap='lg') }}

{{ card(type='feature', title='New Graduate', content='Start with fundamentals and build up systematically', link='/front-matter/roadmap/#new-graduate-line') }}

{{ card(type='feature', title='Senior Engineer', content='Deep dive into all axioms and advanced patterns', link='/front-matter/roadmap/#senior-ic-line') }}

{{ card(type='feature', title='Manager', content='Focus on trade-offs and decision frameworks', link='/front-matter/roadmap/#engineering-manager-line') }}

{{ card(type='feature', title='Express Route', content='Solve your immediate problem', link='/front-matter/roadmap/#express-route') }}

{{ endgrid() }}

## The Foundation: Eight Axioms

Everything in distributed systems emerges from these eight fundamental constraints:

{{ grid(columns=2, gap='md') }}

{{ card(title='1. Latency', content='Information cannot travel faster than light', link='/part1-axioms/axiom1-latency/') }}

{{ card(title='2. Finite Capacity', content='Every resource has limits', link='/part1-axioms/axiom2-capacity/') }}

{{ card(title='3. Failure', content='Components will fail, networks will partition', link='/part1-axioms/axiom3-failure/') }}

{{ card(title='4. Concurrency', content='Multiple things happen at once', link='/part1-axioms/axiom4-concurrency/') }}

{{ card(title='5. Coordination', content='Agreement requires communication', link='/part1-axioms/axiom5-coordination/') }}

{{ card(title='6. Observability', content='You cannot debug what you cannot see', link='/part1-axioms/axiom6-observability/') }}

{{ card(title='7. Human Interface', content='Systems must be operable by humans under stress', link='/part1-axioms/axiom7-human/') }}

{{ card(title='8. Economics', content='Every decision has a cost', link='/part1-axioms/axiom8-economics/') }}

{{ endgrid() }}

## Why This Approach?

<div class="approach-comparison">
  <div class="traditional">
    <h3>❌ Traditional Approach</h3>
    <ul>
      <li>Here's MapReduce</li>
      <li>Here's Paxos</li>
      <li>Here's Consistent Hashing</li>
      <li><em>"But when do I use each?"</em></li>
    </ul>
  </div>
  
  <div class="our-approach">
    <h3>✅ Our Approach</h3>
    <ul>
      <li>Light has finite speed</li>
      <li>Therefore: coordination is expensive</li>
      <li>Therefore: minimize coordination</li>
      <li>Options derived from physics</li>
    </ul>
  </div>
</div>

## What You'll Learn

- **Derive patterns** from first principles, not memorize them
- **Quantify trade-offs** with actual calculations
- **Predict failures** before they happen
- **Design systems** that work with physics, not against it

## Interactive Tools

<div class="tools-preview">
  <a href="/tools/latency-calculator/" class="tool-card">
    <span class="tool-icon">⏱️</span>
    <span class="tool-name">Latency Calculator</span>
  </a>
  
  <a href="/tools/capacity-planner/" class="tool-card">
    <span class="tool-icon">📊</span>
    <span class="tool-name">Capacity Planner</span>
  </a>
  
  <a href="/tools/failure-simulator/" class="tool-card">
    <span class="tool-icon">💥</span>
    <span class="tool-name">Failure Simulator</span>
  </a>
  
  <a href="/tools/cost-calculator/" class="tool-card">
    <span class="tool-icon">💰</span>
    <span class="tool-name">Cost Calculator</span>
  </a>
</div>

## Start Your Journey

<div class="cta-section">
  <a href="/front-matter/preface/" class="cta-button primary">
    Read the Preface
  </a>
  
  <a href="/part1-axioms/" class="cta-button secondary">
    Jump to Axioms
  </a>
  
  <a href="/patterns/decision-tree/" class="cta-button secondary">
    Decision Tree
  </a>
</div>

---

<div class="footer-quote">
  <p><em>"In distributed systems, the impossible becomes merely difficult, and the difficult becomes a career."</em></p>
</div>

<style>
.hero-section {
  text-align: center;
  padding: 3rem 0;
  margin-bottom: 2rem;
}

.hero-quote {
  font-size: 1.3rem;
  color: var(--md-default-fg-color--light);
  font-style: italic;
}

.approach-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin: 2rem 0;
}

.traditional, .our-approach {
  padding: 1.5rem;
  border-radius: 8px;
  border: 2px solid;
}

.traditional {
  background: #fef2f2;
  border-color: #ef4444;
}

.our-approach {
  background: #f0fdf4;
  border-color: #10b981;
}

[data-md-color-scheme="slate"] .traditional {
  background: #2a1a1a;
  border-color: #dc2626;
}

[data-md-color-scheme="slate"] .our-approach {
  background: #1a2f23;
  border-color: #059669;
}

.tools-preview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin: 2rem 0;
}

.tool-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--md-code-bg-color);
  border-radius: 8px;
  text-decoration: none;
  color: var(--md-default-fg-color);
  transition: all 0.2s ease;
  border: 1px solid var(--md-default-fg-color--lightest);
}

.tool-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.tool-icon {
  font-size: 2rem;
}

.cta-section {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin: 3rem 0;
}

.cta-button {
  padding: 1rem 2rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.2s ease;
  display: inline-block;
}

.cta-button.primary {
  background: var(--md-primary-fg-color);
  color: white;
}

.cta-button.secondary {
  background: transparent;
  color: var(--md-primary-fg-color);
  border: 2px solid var(--md-primary-fg-color);
}

.cta-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.footer-quote {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
  color: var(--md-default-fg-color--light);
}
</style>