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

# Validate navigation structure
python3 scripts/check-navigation.py
```

## Architecture & Key Files

### Core Structure
- `mkdocs.yml` - Main configuration defining site structure, theme, plugins, and navigation
- `requirements.txt` - Python dependencies for MkDocs and plugins
- `.github/workflows/deploy.yml` - GitHub Actions workflow for automatic deployment to GitHub Pages
- `docs/` - All documentation content organized hierarchically:
  - `introduction/` - Getting started guides and learning paths
  - `part1-axioms/` - 7 fundamental laws (Correlated Failure, Asynchronous Reality, Emergent Chaos, etc.)
  - `part2-pillars/` - 5 foundational pillars (Work, State, Truth, Control, Intelligence)
  - `patterns/` - Modern architectural patterns (CQRS, Event Sourcing, Service Mesh, etc.)
  - `quantitative/` - Mathematical toolkit (Little's Law, Queueing Theory, Scaling Laws, etc.)
  - `human-factors/` - Operational excellence (SRE, Chaos Engineering, Observability, etc.)
  - `reference/` - Glossary, cheat sheets, recipe cards, security considerations
  - `stylesheets/extra.css` - Extensive custom styling (should be avoided unless really required)

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
1. New law/pillar pages go in respective directories with `index.md`, `examples.md`, `exercises.md`
2. Update navigation in `mkdocs.yml`
3. Use established visual components (axiom-box, decision-box, etc.)
4. Follow existing markdown patterns for consistency

### Deployment
- Push to main branch triggers automatic deployment
- Manual deploy: `mkdocs gh-deploy` (requires permissions)
- Build artifacts in `site/` directory (gitignored)

## Content Quality Standards

### Comprehensive Content Updates
**CRITICAL**: When making any change to a page, think comprehensively:
1. Update the ENTIRE page for consistency and flow
2. Review and update ALL related content across the site
3. Ensure changes align with the overall pedagogical approach
4. Verify cross-references and internal links remain accurate
5. Check related pages in same section AND cross-cutting concerns

### Content Density & Quality Requirements
- **Dense, focused content**: Every sentence must add value
- **Tables over text**: Use comparison tables for feature comparisons, trade-offs, and structured information
- **Diagrams over descriptions**: Prefer Mermaid diagrams, flowcharts, and visual representations over lengthy explanations
- **Minimal verbose text**: Eliminate unnecessary words, redundant explanations, and filler content
- **No unnecessary code**: Only include code when it directly illustrates a concept; prefer architectural diagrams and decision trees

### Visual Content Hierarchy
1. **Mermaid diagrams** for system architectures, decision flows, and complex relationships
2. **Comparison tables** for trade-offs, feature matrices, and structured comparisons  
3. **Custom component boxes** (axiom-box, decision-box, failure-vignette, truth-box) for key insights
4. **Bullet points and numbered lists** for processes and hierarchical information
5. **Minimal prose** only when necessary for context or transitions

### Distributed Systems Specific Quality Standards

#### For Axioms (Part 1)
- **Physics derivation**: Start with fundamental physics constraint (speed of light, thermodynamics)
- **Mathematical foundation**: Include relevant formulas and proofs
- **Failure cascade**: Show how violating the axiom leads to system failure
- **Pattern connections**: Link to patterns that address this axiom

#### For Pillars (Part 2)
- **Distribution strategies table**: Compare centralized vs distributed approaches
- **Trade-off matrix**: Show CAP/PACELC implications
- **Architecture diagrams**: Visual representation of distribution patterns
- **Real-world examples**: Production systems implementing the pillar

#### For Patterns
- **Problem-Solution format**: Clear problem statement → solution approach
- **Architecture diagram**: Visual representation using Mermaid
- **Decision criteria table**: When to use vs when not to use
- **Implementation considerations**: Key technical challenges and solutions

#### For Quantitative Topics
- **Interactive calculators**: Embed calculation tools where applicable
- **Formula derivations**: Show mathematical proofs concisely
- **Visual representations**: Graphs, charts for scaling laws and distributions
- **Real-world benchmarks**: Actual performance numbers from production systems

### Content Update Checklist
Before committing any content change, verify:
- [ ] Entire page reviewed for consistency
- [ ] Related pages updated (same pillar/axiom, cross-references)
- [ ] All examples use consistent scenario/domain
- [ ] Diagrams and tables prioritized over text
- [ ] No redundant explanations or verbose descriptions
- [ ] Visual components (boxes) used appropriately
- [ ] Cross-links to axioms/pillars verified
- [ ] Failure stories integrated where relevant
- [ ] Multiple audience perspectives considered

## Content Guidelines

### When Writing Documentation
1. **Start with visuals**: Lead with diagrams, tables, or structured layouts
2. **Physics-first derivation**: Derive patterns from fundamental constraints
3. **Real failure integration**: Include production disaster case studies with each concept
4. **Cross-reference ruthlessly**: Link to related axioms, pillars, and patterns
5. **Multiple perspectives**: Address different audience needs (new grads, seniors, managers)

### Content Structure Standards
- **Scannable format**: Headers, bullets, tables, diagrams
- **Layered depth**: Summary → Details → Examples → Exercises
- **Interactive elements**: Decision trees, calculators, interactive diagrams where possible
- **Consistent terminology**: Use established glossary terms and maintain consistency

## Project Roadmap (from IMPROVEMENTS.md)

Key planned enhancements:
1. **Security Pillar**: Add 6th pillar for distributed systems security
2. **Interactive Tools**: Expand beyond calculators to simulators
3. **End-to-End Case Study**: Ride-sharing app applying all concepts
4. **Granular Navigation**: Break up monolithic pages into smaller sections
5. **Learning Reinforcement**: Quizzes, flashcards, capstone project

## Important Notes

### Lint and Testing
Currently, there are no automated linting or testing commands for the documentation. When modifying content:
- Manually verify Markdown syntax is correct
- Check that Mermaid diagrams render properly using `mkdocs serve`
- Validate navigation changes with `python3 scripts/check-navigation.py`

### Project Statistics
- **800+ Visual Diagrams**: Created using Mermaid for maximum clarity
- **330+ Cross-References**: Extensive interlinking between concepts
- **100+ Files**: Enhanced with visual-first approach
- **40+ Case Studies**: Real-world production failure stories