# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a MkDocs-based documentation site called "The Compendium of Distributed Systems" - an educational resource that teaches distributed systems from first principles, starting with physics and mathematics rather than specific technologies.

## Essential Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server (access at http://127.0.0.1:8000)
mkdocs serve

# Build static site
mkdocs build

# Deploy to GitHub Pages (only from main branch)
mkdocs gh-deploy

# Clean build artifacts
rm -rf site/
```

## Architecture & Key Files

### Core Structure
- `mkdocs.yml` - Main configuration defining site structure, theme, plugins, and navigation
- `requirements.txt` - Python dependencies for MkDocs and plugins
- `.github/workflows/deploy.yml` - GitHub Actions workflow for automatic deployment to GitHub Pages
- `automation/` - Scripts for site maintenance and content validation
  - `fix_broken_links.py` - Script to fix common broken links
  - `validate_links.py` - Script to check for broken links
  - `generate_site_tree.py` - Script to generate site structure
  - And many more utility scripts
- `artifacts/` - Generated reports and analysis files
- `docs/` - All documentation content organized hierarchically:
  - `introduction/` - Getting started guides and learning paths
  - `part1-axioms/` - 7 fundamental laws (Correlated Failure, Asynchronous Reality, Emergent Chaos, etc.)
  - `part2-pillars/` - 5 foundational pillars (Work, State, Truth, Control, Intelligence)
  - `patterns/` - Modern architectural patterns (CQRS, Event Sourcing, Service Mesh, etc.)
  - `quantitative/` - Mathematical toolkit (Little's Law, Queueing Theory, Scaling Laws, etc.)
  - `human-factors/` - Operational excellence (SRE, Chaos Engineering, Observability, etc.)
  - `reference/` - Glossary, cheat sheets, recipe cards, security considerations
  - `tools/` - Interactive calculators
  - `stylesheets/extra.css` - Extensive custom styling

### Content Philosophy
The documentation follows a unique pedagogical approach:
1. **7 Fundamental Laws**: Correlated Failure, Asynchronous Reality, Emergent Chaos, Multidimensional Optimization, Distributed Knowledge, Cognitive Load, Economic Reality
2. **5 Foundational Pillars**: Work Distribution, State Distribution, Truth Distribution, Control Distribution, Intelligence Distribution
3. **Physics-first**: Derives patterns from speed of light and thermodynamics
4. **Multiple learning paths**: Tailored for new grads, senior engineers, managers, and express learners
5. **Real failure stories**: Production disaster case studies

### Visual Components
The site uses custom-styled components defined in `extra.css`:
- `.axiom-box` - Purple-themed boxes for fundamental principles
- `.decision-box` - Green-themed boxes for decision frameworks
- `.failure-vignette` - Red-themed boxes for failure stories
- `.truth-box` - Blue-themed boxes for insights
- `.journey-container` - Interactive journey map on homepage
- `.grid.cards` - Navigation card layout

### Design System
- Primary color: Indigo (#5448C8)
- Accent color: Cyan (#00BCD4)
- Typography: Inter for body, JetBrains Mono for code
- 8px grid system for spacing
- Responsive design with mobile considerations
- Dark mode support with slate color scheme

## Important Configuration

### GitHub Pages Deployment
- Repository: `deepaucksharma/DStudio`
- Main branch: `main`
- GitHub Actions automatically builds and deploys on push to main
- Site URL: https://deepaucksharma.github.io/DStudio/

### MkDocs Configuration
- Theme: Material for MkDocs v9.4.0+
- Key plugins:
  - `mermaid2` - For diagram rendering
  - `search` - Full-text search functionality
- Markdown extensions:
  - `pymdownx` suite for enhanced markdown (tabs, admonitions, superfences)
  - `mermaid` custom fence for diagrams
  - Code highlighting with line numbers
  - Emoji support via twemoji

## Development Workflow

### Local Development
1. Install dependencies: `pip install -r requirements.txt`
2. Start dev server: `mkdocs serve`
3. Make changes (auto-reload enabled)
4. View at http://127.0.0.1:8000

### Adding Content
1. New axiom/pillar pages go in respective directories with `index.md`, `examples.md`, `exercises.md`
2. Update navigation in `mkdocs.yml`
3. Use established visual components (axiom-box, decision-box, etc.)
4. Follow existing markdown patterns for consistency

### Deployment
- Push to main branch triggers automatic deployment
- Manual deploy: `mkdocs gh-deploy` (requires permissions)
- Build artifacts in `site/` directory (gitignored)

## Content Guidelines

### When Writing Documentation
1. Use Mermaid diagrams for complex concepts
2. Include practical examples with each theoretical concept
3. Add failure stories to illustrate real-world implications
4. Use appropriate visual component boxes for different content types
5. Keep the physics-first approach - derive patterns from constraints

### Code Examples
- Use language-specific syntax highlighting
- Include both correct and incorrect approaches
- Show trade-offs explicitly
- Reference specific axioms/pillars when applicable

## Project Roadmap (from IMPROVEMENTS.md)

Key planned enhancements:
1. **Security Pillar**: Add 6th pillar for distributed systems security
2. **Interactive Tools**: Expand beyond calculators to simulators
3. **End-to-End Case Study**: Ride-sharing app applying all concepts
4. **Granular Navigation**: Break up monolithic pages into smaller sections
5. **Learning Reinforcement**: Quizzes, flashcards, capstone project