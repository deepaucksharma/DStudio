---
title: Admonition Semantic Guide
description: Standardized usage of admonitions across the Compendium for visual consistency
type: reference
difficulty: beginner
reading_time: 5 min
prerequisites: []
status: complete
last_updated: 2025-07-25
---

# Admonition Semantic Guide

This guide defines the standardized semantic usage of admonitions throughout The Compendium of Distributed Systems.

## Semantic Rules for Admonition Usage

### `!!! abstract` - High-Level Summaries
**Use for**: Executive summaries, key takeaways, pattern overviews
**Color**: Light blue
**Example contexts**:
- Pattern summaries at the beginning of a section
- High-level architectural overviews
- Key takeaways at the end of a topic

### `!!! info` - General Information
**Use for**: Contextual information, background, neutral facts
**Color**: Blue
**Example contexts**:
- Pattern origins and history
- Industry standards and defaults
- General explanations and context

### `!!! tip` - Best Practices
**Use for**: Recommendations, optimization suggestions, pro tips
**Color**: Green
**Example contexts**:
- Production-ready configurations
- Performance optimization advice
- Recommended approaches

### `!!! warning` - Important Caveats
**Use for**: Things to be careful about, potential issues, limitations
**Color**: Orange
**Example contexts**:
- Common pitfalls to avoid
- Performance implications
- Configuration warnings

### `!!! danger` - Critical Issues
**Use for**: Serious problems, data loss risks, system failures
**Color**: Red
**Example contexts**:
- Production outage scenarios
- Data corruption risks
- Security vulnerabilities

### `!!! example` - Code Examples
**Use for**: Code demonstrations, implementation samples
**Color**: Purple
**Example contexts**:
- Code snippets
- Configuration examples
- Real-world implementations

### `!!! quote` - Citations
**Use for**: Quotes from experts, papers, or documentation
**Color**: Gray
**Example contexts**:
- Expert opinions
- Academic citations
- Official documentation quotes

### `!!! success` - Positive Outcomes
**Use for**: Success stories, achievements, positive results
**Color**: Green
**Example contexts**:
- Successful implementations
- Performance improvements
- Problem resolutions

### `!!! question` - Exercises
**Use for**: Thought experiments, exercises, reader challenges
**Color**: Light green
**Example contexts**:
- End-of-section exercises
- Thought-provoking questions
- Interactive challenges

### `!!! failure` - Failure Stories
**Use for**: Production disasters, outage stories, lessons from failures
**Color**: Red
**Example contexts**:
- Real-world outage descriptions
- Post-mortem summaries
- Failure case studies

## Deprecated Admonitions

### ❌ `!!! note` 
**Status**: Deprecated
**Action**: Replace with more specific types above
**Reason**: Too generic, doesn't convey semantic meaning

## Examples

### Before (Inconsistent)
```markdown
!!! note "Circuit Breaker Origin"
    The Circuit Breaker pattern was popularized by Michael Nygard...

!!! info "Production Monitoring Dashboard"
    Circuit Breaker Health Status...
```

### After (Consistent)
```markdown
!!! info "Pattern Origin"
    The Circuit Breaker pattern was popularized by Michael Nygard...

!!! success "Production Monitoring Dashboard"
    Circuit Breaker Health Status...
```

## Quick Reference Table

| Type | Use Case | Semantic Meaning |
|------|----------|------------------|
| `abstract` | Summaries | High-level overview |
| `info` | Context | General information |
| `tip` | Best practices | Recommendations |
| `warning` | Cautions | Important limitations |
| `danger` | Critical issues | Serious risks |
| `example` | Code/demos | Implementation examples |
| `quote` | Citations | External references |
| `success` | Achievements | Positive outcomes |
| `question` | Exercises | Reader engagement |
| `failure` | Disasters | Lessons from failures |

---

<div class="page-nav" markdown>
[:material-arrow-left: Reference Index](../reference/tags.md) | 
[:material-arrow-up: Reference](../reference/tags.md)
</div>