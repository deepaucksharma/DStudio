# The Compendium of Distributed Systems

<div style="text-align: center; margin: 2rem 0 3rem 0;">
    <p style="font-size: 1.5rem; font-weight: 300; line-height: 1.6; color: var(--md-default-fg-color--light); max-width: 800px; margin: 0 auto;">
        A first-principles approach to understanding distributed systems, deriving patterns from fundamental physical and mathematical constraints rather than memorizing solutions.
    </p>
</div>

---

## 🚀 Quick Navigation

<div class="grid cards" markdown>

- :material-book-open-page-variant:{ .lg .middle } **[Start Reading →](distributed-systems-book.md)**

    ---

    Dive into the complete compendium and begin your journey from first principles

- :material-map:{ .lg .middle } **[Learning Paths →](distributed-systems-book.md#page-iv-reader-road-map)**

    ---

    Choose a customized path based on your role and experience level

- :material-lightbulb:{ .lg .middle } **[Key Concepts →](#-what-youll-learn)**

    ---

    Explore the 8 fundamental axioms that govern all distributed systems

- :material-github:{ .lg .middle } **[Contribute →](https://github.com/deepaucksharma/DStudio)**

    ---

    Join our community and help improve this resource

</div>

## 🎯 Our Philosophy

This project takes a unique approach to teaching distributed systems:

- **Physics First**: We start with the speed of light, not with Kafka
- **Math Over Mythology**: Quantitative trade-offs replace "best practices"
- **Failures as Teachers**: Real production disasters illuminate principles
- **Derive, Don't Memorize**: Every pattern emerges from fundamental constraints

## 🏗️ Project Structure

```
DStudio/
├── docs/                    # Documentation source files
│   ├── distributed-systems-book.md  # Main content
│   ├── index.md            # Homepage
│   └── stylesheets/        # Custom styling
│       └── extra.css       # Visual enhancements
├── mkdocs.yml              # MkDocs configuration
└── requirements.txt        # Python dependencies
```

## 🚀 Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/deepaucksharma/DStudio.git
   cd DStudio
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run locally**:
   ```bash
   mkdocs serve
   ```
   Visit `http://127.0.0.1:8000` to see your changes live.

## 📖 Content Overview

The compendium covers:

- **8 Fundamental Axioms**: Core constraints that govern all distributed systems
- **Decision Frameworks**: Quantitative tools for architectural choices
- **Failure Vignettes**: Learn from real production disasters
- **Interactive Exercises**: Hands-on learning in under 5 minutes

## 🎓 Who Is This For?

<div class="grid cards" markdown>

- :material-school:{ .lg .middle } **New Graduates**

    ---
    
    Build a solid foundation with physics-based mental models that will serve you throughout your career

- :material-code-tags:{ .lg .middle } **Senior Engineers**

    ---
    
    Deepen your understanding and learn to articulate trade-offs with mathematical precision

- :material-account-group:{ .lg .middle } **Engineering Managers**

    ---
    
    Make better architectural decisions and communicate effectively with your team

- :material-rocket-launch:{ .lg .middle } **Startup Founders**

    ---
    
    Avoid common pitfalls and build systems that can scale with your business

</div>

## 📚 What You'll Learn

<div class="axiom-box animate-fadeIn">

### The Eight Fundamental Axioms

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1.5rem;">

<div>
<h4 style="color: var(--primary-color); margin: 0;">⚡ Latency</h4>
<p style="margin: 0.5rem 0; font-size: 0.9rem;">Speed of light is non-negotiable</p>
</div>

<div>
<h4 style="color: var(--primary-color); margin: 0;">📦 Finite Capacity</h4>
<p style="margin: 0.5rem 0; font-size: 0.9rem;">Every resource has a breaking point</p>
</div>

<div>
<h4 style="color: var(--primary-color); margin: 0;">💥 Failure</h4>
<p style="margin: 0.5rem 0; font-size: 0.9rem;">Components will fail; plan accordingly</p>
</div>

<div>
<h4 style="color: var(--primary-color); margin: 0;">⚖️ Consistency</h4>
<p style="margin: 0.5rem 0; font-size: 0.9rem;">You can't have your cake and eat it too</p>
</div>

<div>
<h4 style="color: var(--primary-color); margin: 0;">⏰ Time</h4>
<p style="margin: 0.5rem 0; font-size: 0.9rem;">There is no "now" in distributed systems</p>
</div>

<div>
<h4 style="color: var(--primary-color); margin: 0;">🔄 Ordering</h4>
<p style="margin: 0.5rem 0; font-size: 0.9rem;">Events happen, but in what order?</p>
</div>

<div>
<h4 style="color: var(--primary-color); margin: 0;">🧩 Knowledge</h4>
<p style="margin: 0.5rem 0; font-size: 0.9rem;">Partial information is the only information</p>
</div>

<div>
<h4 style="color: var(--primary-color); margin: 0;">📈 Growth</h4>
<p style="margin: 0.5rem 0; font-size: 0.9rem;">Systems evolve or die</p>
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

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 1.5rem;">

<div>
<h4 style="margin: 0 0 0.5rem 0;">📊 The Math</h4>

- 2 servers = 1 connection
- 5 servers = 10 connections  
- 10 servers = 45 connections
- n servers = n(n-1)/2 connections

**Coordination cost**: O(n²)  
**Capacity growth**: O(n)
</div>

<div>
<h4 style="margin: 0 0 0.5rem 0;">💡 The Lesson</h4>

Sometimes the best distributed system is the one that isn't distributed. Before adding complexity:

1. **Optimize** what you have
2. **Measure** actual bottlenecks
3. **Calculate** coordination overhead
4. **Consider** vertical scaling first
</div>

</div>

</div>

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This work is licensed under CC-BY-NC with "Derivative Works Encouraged" clause.

---

<div style="text-align: center; margin: 3rem 0;">
    <a href="distributed-systems-book.md" class="md-button md-button--primary" style="font-size: 1.1rem; padding: 0.8rem 2rem;">
        Begin Your Journey →
    </a>
</div>

<div style="text-align: center; color: var(--md-default-fg-color--light); font-size: 0.9rem; margin-top: 2rem;">
    Built with ❤️ using <a href="https://squidfunk.github.io/mkdocs-material/">Material for MkDocs</a>
</div>