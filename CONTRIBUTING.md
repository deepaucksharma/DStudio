# Contributing to DStudio

Thank you for your interest in contributing to DStudio - The Compendium of Distributed Systems!

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Install dependencies: `pip install -r requirements.txt`
4. Make your changes
5. Test locally: `mkdocs serve`
6. Submit a pull request

## Guidelines

### Content Guidelines

- Maintain the visual-first approach
- Use Mermaid diagrams for complex concepts
- Follow established visual patterns
- Add cross-references where relevant
- Include practical examples with theoretical concepts
- Add failure stories to illustrate real-world implications

### Technical Guidelines

- Keep changes simple and focused
- Test your changes locally before submitting
- Follow standard Markdown formatting
- Use clear, descriptive commit messages
- Run validation scripts before submitting PRs

## Project Structure

```
docs/
├── introduction/       # Getting started and philosophy
├── part1-axioms/       # 7 fundamental laws
├── part2-pillars/      # 5 foundational pillars
├── patterns/           # Distributed system patterns
├── case-studies/       # Real-world examples
├── quantitative/       # Mathematical models
├── human-factors/      # Operational excellence
├── reference/          # Glossary and cheat sheets
└── tools/              # Interactive calculators
```

## Development Setup

```bash
# Clone the repository
git clone https://github.com/deepaucksharma/DStudio.git
cd DStudio

# Install dependencies
pip install -r requirements.txt

# Start development server
mkdocs serve
```

Visit http://127.0.0.1:8000 to see your changes in real-time.

## Validation Tools

We have several scripts in the `automation/` directory to help validate content:

```bash
# Check for broken links
python automation/validate_links.py

# Fix common broken links
python automation/fix_broken_links.py

# Generate site structure report
python automation/generate_site_tree.py
```

## Questions?

Feel free to open an issue if you have any questions!