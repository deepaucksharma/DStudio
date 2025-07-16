# The Compendium of Distributed Systems 📚

A first-principles approach to understanding distributed systems, deriving patterns from fundamental physical and mathematical constraints rather than memorizing solutions.

## 🌐 Live Documentation

Visit the live documentation: [https://deepaucksharma.github.io/DStudio/](https://deepaucksharma.github.io/DStudio/)

## 🎯 Philosophy

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

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This work is licensed under CC-BY-NC with "Derivative Works Encouraged" clause.

---

Built with ❤️ using [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)

*Begin your journey with [The Compendium →](distributed-systems-book.md)*