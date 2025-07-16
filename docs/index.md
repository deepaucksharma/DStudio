# The Compendium of Distributed Systems

<div style="text-align: center; margin: 2rem 0;">
    <h2 style="font-size: 2rem; color: var(--md-primary-fg-color); margin-bottom: 1rem;">
        A First-Principles Approach to Understanding Distributed Systems
    </h2>
    <p style="font-size: 1.2rem; color: var(--md-default-fg-color--light);">
        From Physics to Production: Building Systems That Scale
    </p>
</div>

---

## 🚀 Start Your Journey

<div class="grid cards" markdown>

- :material-book-open-variant:{ .lg .middle } **[Read the Compendium](distributed-systems-book.md)**

    ---

    Dive into our comprehensive guide that derives distributed systems patterns from fundamental physical and mathematical constraints.

    [:octicons-arrow-right-24: Begin Reading](distributed-systems-book.md)

- :material-chart-timeline:{ .lg .middle } **Choose Your Path**

    ---

    Whether you're a new grad, senior engineer, or engineering manager, we have a learning path designed for you.

    [:octicons-arrow-right-24: View Learning Paths](distributed-systems-book.md#page-iv-reader-road-map)

</div>

## 🎯 Core Philosophy

!!! quote "First Principles Thinking"
    "We don't start with Kafka or Kubernetes. We start with the speed of light and the laws of thermodynamics. Every pattern emerges from inescapable constraints."
## 📚 What You'll Learn

<div class="axiom-box" style="margin: 2rem 0;">

### The Eight Fundamental Axioms

1. **Latency** - Speed of light is non-negotiable
2. **Finite Capacity** - Every resource has a breaking point
3. **Failure** - Components will fail; plan accordingly
4. **Consistency** - You can't have your cake and eat it too
5. **Time** - There is no "now" in distributed systems
6. **Ordering** - Events happen, but in what order?
7. **Knowledge** - Partial information is the only information
8. **Growth** - Systems evolve or die

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

## 🚦 Quick Start

!!! success "Your First Insight in 30 Seconds"
    **Question**: Why does adding more servers sometimes make your system slower?
    
    **Answer**: Each server adds coordination overhead. With 2 servers, you have 1 connection. With 10 servers, you have 45 connections. The coordination cost grows as O(n²), while capacity grows as O(n).
    
    **Lesson**: Sometimes the best distributed system is the one that isn't distributed.

---

*Begin your journey with [The Compendium →](distributed-systems-book.md)*