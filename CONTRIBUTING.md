# Contributing to The Compendium of Distributed Systems

First off, thank you for considering contributing to this educational resource! 🎉

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Making Contributions](#making-contributions)
- [Style Guides](#style-guides)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Python 3.8+ (for MkDocs)
- Node.js 16+ (for build tools)
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/deepaucksharma/DStudio.git
cd DStudio

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
npm install

# Start development server
npm run dev

# In another terminal, start asset watching
npm run js:dev
npm run css:dev
```

## Development Setup

### 1. Fork and Clone

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/DStudio.git
cd DStudio
git remote add upstream https://github.com/deepaucksharma/DStudio.git
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Install Dependencies

```bash
# Python dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Node dependencies
npm install
```

### 4. Run Development Server

```bash
# Start MkDocs server (hot-reload enabled)
mkdocs serve

# In another terminal, run asset compilation
npm run js:dev
npm run css:dev
```

## Project Structure

```
DStudio/
├── docs/                    # Documentation content
│   ├── javascripts/        # JavaScript modules
│   │   ├── core/          # Core functionality
│   │   ├── components/    # UI components
│   │   └── tools/         # Interactive tools
│   ├── stylesheets/       # CSS files
│   ├── overrides/         # MkDocs theme overrides
│   └── *.md               # Markdown content
├── tests/                  # Test files
│   ├── unit/              # Unit tests
│   └── e2e/               # End-to-end tests
├── mkdocs.yml             # MkDocs configuration
├── package.json           # Node.js dependencies
├── webpack.config.js      # Build configuration
└── requirements.txt       # Python dependencies
```

## Making Contributions

### Types of Contributions

#### 1. Content Improvements
- Fix typos or grammatical errors
- Improve explanations
- Add examples or diagrams
- Update outdated information

#### 2. New Features
- Interactive tools
- Visualizations
- New axioms/pillars/patterns
- Exercise solutions

#### 3. Bug Fixes
- JavaScript errors
- CSS layout issues
- Broken links
- Build problems

#### 4. Performance Improvements
- Optimize JavaScript
- Reduce bundle size
- Improve load times
- Better caching strategies

### Development Workflow

1. **Check existing issues** - See if someone's already working on it
2. **Create an issue** - Describe what you plan to do
3. **Write code** - Follow our style guides
4. **Add tests** - Ensure your changes work
5. **Update docs** - If needed
6. **Submit PR** - With clear description

## Style Guides

### JavaScript Style Guide

We use ESLint with Airbnb config. Key points:

```javascript
// Good
class LatencyCalculator {
  constructor(options = {}) {
    this.speedOfLight = options.speedOfLight || SPEED_OF_LIGHT_FIBER;
    this.init();
  }
  
  calculate(distance, medium = 'fiber') {
    if (distance <= 0) {
      throw new Error('Distance must be positive');
    }
    
    return (distance / this.getSpeed(medium)) * 1000;
  }
}

// Avoid
function calc(d) {
  return d / 200000 * 1000
}
```

### CSS Style Guide

```css
/* Good */
.tool-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  padding: 1.5rem;
}

.tool-container__input {
  /* BEM naming for elements */
}

.tool-container--loading {
  /* BEM naming for modifiers */
}

/* Avoid */
.toolContainer {
  display:grid;grid-template-columns:1fr 1fr;
}
```

### Markdown Style Guide

```markdown
# Clear Heading

Brief introduction paragraph.

## Section with Code

Explain concept first, then show code:

```python
def calculate_latency(distance_km):
    """Calculate one-way latency in milliseconds."""
    SPEED_OF_LIGHT_FIBER = 200000  # km/s
    return (distance_km / SPEED_OF_LIGHT_FIBER) * 1000
```

!!! note "Important Note"
    Use admonitions for callouts.
```

### Commit Message Format

```
type(scope): subject

body

footer
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `perf`: Performance improvement
- `test`: Add tests
- `chore`: Maintenance

Example:
```
feat(tools): add network topology visualizer

Add interactive tool for visualizing different network topologies
and their trade-offs. Includes ring, mesh, and star configurations.

Closes #123
```

## Testing

### Running Tests

```bash
# All tests
npm test

# Unit tests only
npm run test:unit

# E2E tests only
npm run test:e2e

# With coverage
npm run test:coverage

# Accessibility tests
npm run test:a11y
```

### Writing Tests

#### Unit Tests

```javascript
// tests/unit/calculator.test.js
describe('LatencyCalculator', () => {
  let calculator;
  
  beforeEach(() => {
    calculator = new LatencyCalculator();
  });
  
  test('calculates fiber optic latency correctly', () => {
    const latency = calculator.calculate(1000, 'fiber');
    expect(latency).toBeCloseTo(5, 1);
  });
  
  test('throws error for negative distance', () => {
    expect(() => calculator.calculate(-100)).toThrow();
  });
});
```

#### E2E Tests

```javascript
// tests/e2e/tools.spec.js
describe('Latency Calculator Tool', () => {
  beforeEach(() => {
    cy.visit('/tools/latency-calculator/');
  });
  
  it('calculates RTT when inputs change', () => {
    cy.get('#distance').clear().type('5000');
    cy.get('#hops').clear().type('10');
    
    cy.get('#total-rtt').should('contain', '55');
  });
});
```

## Documentation

### Adding New Pages

1. Create markdown file in appropriate directory
2. Add to `mkdocs.yml` navigation
3. Include required frontmatter:

```yaml
---
title: Your Page Title
description: Brief description for SEO
keywords: [keyword1, keyword2]
---
```

### API Documentation

For JavaScript modules:

```javascript
/**
 * Calculate network latency based on distance and medium.
 * 
 * @param {number} distance - Distance in kilometers
 * @param {string} [medium='fiber'] - Network medium ('fiber', 'copper', 'wireless')
 * @returns {number} One-way latency in milliseconds
 * @throws {Error} If distance is negative
 * 
 * @example
 * const latency = calculateLatency(1000, 'fiber');
 * console.log(latency); // 5
 */
function calculateLatency(distance, medium = 'fiber') {
  // Implementation
}
```

## Submitting Changes

### Pull Request Process

1. **Update your branch**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run checks**
   ```bash
   npm run lint
   npm test
   npm run build
   ```

3. **Push changes**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create Pull Request**
   - Use PR template
   - Link related issues
   - Add screenshots if UI changes
   - Request review

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Manual testing completed

## Screenshots
(if applicable)

## Checklist
- [ ] Code follows style guide
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No console errors
```

## Getting Help

- **Discord**: [Join our community](https://discord.gg/distributed-systems)
- **Issues**: [GitHub Issues](https://github.com/deepaucksharma/DStudio/issues)
- **Discussions**: [GitHub Discussions](https://github.com/deepaucksharma/DStudio/discussions)

## Recognition

Contributors are recognized in:
- [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Release notes
- Project README

Thank you for contributing! 🙏