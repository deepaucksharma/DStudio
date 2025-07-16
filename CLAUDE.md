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

# Deploy to GitHub Pages
mkdocs gh-deploy
```

## Architecture & Key Files

### Core Structure
- `mkdocs.yml` - Main configuration defining site structure, theme, and plugins
- `docs/` - All documentation content
  - `index.md` - Homepage with navigation cards and philosophy
  - `distributed-systems-book.md` - Main content (comprehensive guide with 8 axioms)
  - `stylesheets/extra.css` - Extensive custom styling (784 lines)

### Content Philosophy
The documentation follows a unique pedagogical approach:
1. **8 Fundamental Axioms**: Latency, Finite Capacity, Failure, Consistency, Time, Ordering, Knowledge, Growth
2. **Physics-first**: Derives patterns from speed of light and thermodynamics
3. **Multiple learning paths**: Tailored for new grads, senior engineers, managers, and express learners
4. **Real failure stories**: Production disaster case studies

### Visual Components
The site uses custom-styled components defined in `extra.css`:
- `.axiom-box` - Purple-themed boxes for fundamental principles
- `.decision-box` - Green-themed boxes for decision frameworks
- `.failure-vignette` - Red-themed boxes for failure stories
- `.truth-box` - Blue-themed boxes for insights

### Design System
- Primary color: Indigo (#5448C8)
- Accent color: Cyan (#00BCD4)
- Typography: Inter for body, JetBrains Mono for code
- 8px grid system for spacing
- Responsive design with mobile considerations

## Important Configuration

The site is configured for GitHub Pages deployment:
- Repository: `deepaucksharma/DStudio`
- Main branch: `main`
- GitHub Actions workflow at `.github/workflows/deploy.yml`

## Development Notes

When modifying content:
1. Mermaid diagrams are supported via `mkdocs-mermaid2-plugin`
2. Use pymdown-extensions for enhanced markdown (tabs, admonitions, etc.)
3. Custom CSS classes are available for special content boxes
4. Material theme features enabled: navigation.instant, content.code.copy, etc.

When updating styles:
1. CSS variables are defined for consistent theming
2. Dark mode is fully supported with slate color scheme
3. Accessibility features are included (focus states, high contrast)
4. Print styles are defined for PDF generation