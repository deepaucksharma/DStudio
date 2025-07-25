# DStudio - The Compendium of Distributed Systems

A comprehensive, visual-first learning platform for distributed systems, teaching from first principles through physics and mathematics rather than specific technologies.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start development server
mkdocs serve

# Visit http://127.0.0.1:8000
```

## 📚 What is DStudio?

DStudio is an educational resource that teaches distributed systems through:

- **7 Fundamental Laws**: Starting from physics (speed of light, thermodynamics)
- **5 Foundational Pillars**: Building up to practical system design
- **30+ Patterns**: Modern architectural patterns with visual explanations
- **40+ Case Studies**: Real-world systems analyzed and visualized
- **800+ Visual Diagrams**: Complex concepts made accessible

## 🎨 Visual-First Approach

This documentation has been transformed to prioritize visual learning:

- **Mermaid Diagrams**: Flowcharts, sequence diagrams, state machines
- **Architecture Visualizations**: System designs and data flows
- **Mathematical Concepts**: Formulas and graphs made intuitive
- **Cross-References**: 330+ interconnections between concepts

## 📖 Content Structure

```
docs/
├── index.md                    # Homepage with navigation
├── introduction/               # Getting started and philosophy
├── part1-axioms/              # 7 fundamental laws
│   ├── axiom1-latency/        # Latency constraints
│   ├── axiom2-capacity/       # Finite capacity
│   ├── axiom3-failure/        # Partial failure
│   └── ...
├── part2-pillars/             # 5 foundational pillars
│   ├── work/                  # Work distribution
│   ├── state/                 # State management
│   ├── truth/                 # Distributed truth
│   ├── control/               # Control flow
│   └── intelligence/          # Learning systems
├── patterns/                  # 30+ distributed patterns
├── case-studies/              # 40+ real-world examples
├── quantitative/              # Mathematical models
├── human-factors/             # Operational excellence
├── reference/                 # Glossary and cheat sheets
└── tools/                     # Interactive calculators
```

## 🛠️ Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server (auto-reload enabled)
mkdocs serve

# Build static site
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

### Project Structure

```
.
├── docs/                 # Documentation content
├── project-docs/         # Project documentation and reports
├── scripts/              # Maintenance and conversion scripts
├── archive/              # Archived configurations
├── automation/           # Build and deployment scripts
├── artifacts/            # Generated artifacts
├── mkdocs.yml           # MkDocs configuration
├── requirements.txt     # Python dependencies
├── CLAUDE.md            # AI assistant instructions
└── README.md            # This file
```

### Key Files

- `mkdocs.yml` - Site configuration with Material theme
- `requirements.txt` - Python dependencies
- `CLAUDE.md` - AI assistant instructions
- `PROJECT_DOCUMENTATION.md` - Consolidated project docs

## 🎯 Learning Paths

The documentation supports multiple learning approaches:

1. **New Graduate Path**: Start with axioms, build up slowly
2. **Senior Engineer Path**: Jump to patterns and case studies
3. **Manager Path**: Focus on trade-offs and human factors
4. **Express Path**: Quick overview of key concepts

## ✨ Features

- **Progressive Disclosure**: Content complexity increases gradually
- **Real Failure Stories**: Learn from production disasters
- **Interactive Elements**: Calculators and decision trees
- **Multiple Perspectives**: Same concept explained different ways
- **Mobile Responsive**: Works on all devices

## 📊 Visual Conversion Statistics

- **100+ files** enhanced with visuals
- **800+ diagrams** created using Mermaid
- **10,000+ lines** of code replaced with diagrams
- **330+ cross-references** linking related concepts

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Key principles:
- Maintain visual-first approach
- Use Mermaid for diagrams
- Follow established visual patterns
- Add cross-references where relevant

## 📚 Documentation

All project documentation has been organized in the `project-docs/` directory:
- Implementation reports and summaries
- Optimization guides and plans
- Consistency reports and checklists

See [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) for details.

## 🌐 Deployment

The site is automatically deployed to GitHub Pages:
- Repository: `deepaucksharma/DStudio`
- URL: https://deepaucksharma.github.io/DStudio/

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

*"Understanding distributed systems starts with understanding the constraints of physics."*