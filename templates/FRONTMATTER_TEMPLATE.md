# YAML Frontmatter Template

This document defines the standard YAML frontmatter that should be used across all documentation files in the Compendium.

## Standard Frontmatter Structure

```yaml
---
title: "Page Title"
description: "Brief description of the page content (150-160 characters for SEO)"
date: 2024-01-15
modified: 2024-01-15
authors:
  - Author Name
category: "axioms|pillars|patterns|case-studies|human-factors|reference"
tags:
  - distributed-systems
  - relevant-tag
  - another-tag
difficulty: "beginner|intermediate|advanced|expert"
reading_time: "10 min"
prerequisites:
  - /part1-axioms/axiom1-latency/
  - /part2-pillars/state/
related:
  - /patterns/circuit-breaker/
  - /case-studies/#netflix
toc: true
draft: false
weight: 10
---
```

## Field Descriptions

### Required Fields

- **title**: The main title of the page (used in navigation and SEO)
- **description**: Brief description for search engines and previews
- **category**: Primary category for organization
- **difficulty**: Expected reader expertise level

### Optional Fields

- **date**: Original publication date (YYYY-MM-DD format)
- **modified**: Last modification date
- **authors**: List of content authors
- **tags**: Keywords for search and categorization
- **reading_time**: Estimated reading time
- **prerequisites**: Links to required prior knowledge
- **related**: Links to related content
- **toc**: Whether to show table of contents (default: true)
- **draft**: Whether this is draft content (default: false)
- **weight**: Sort order within category (lower numbers first)

## Category-Specific Templates

### Law Pages

```yaml
---
title: "Law N: [Name]"
description: "Fundamental constraint of distributed systems: [brief description]"
category: "axioms"
axiom_number: N
axiom_name: "Short Name"
key_principle: "One-line summary of the axiom"
tags:
  - fundamental-constraints
  - [specific-aspect]
difficulty: "beginner"
---
```

### Pattern Pages

```yaml
---
title: "[Pattern Name] Pattern"
description: "Distributed systems pattern for [solving what problem]"
category: "patterns"
pattern_type: "resilience|data|coordination|operational"
problem_solved: "Brief problem statement"
when_to_use: "Brief guidance on when to apply"
when_not_to_use: "Brief guidance on when to avoid"
tags:
  - design-patterns
  - [specific-technique]
difficulty: "intermediate"
---
```

### Case Study Pages

```yaml
---
title: "[Company]: [System Name]"
description: "How [Company] built [what] to handle [scale/challenge]"
category: "case-studies"
company: "Company Name"
industry: "Technology|Finance|Retail|etc"
scale: "Users/requests/data volume"
key_technologies:
  - Technology 1
  - Technology 2
year: 2024
tags:
  - real-world
  - [specific-technology]
  - scale
difficulty: "intermediate"
---
```

### Exercise Pages

```yaml
---
title: "[Topic] Exercises"
description: "Hands-on exercises for understanding [topic]"
category: "exercises"
exercise_type: "labs|problems|projects"
estimated_time: "2 hours"
required_tools:
  - Python 3.8+
  - Docker
learning_objectives:
  - Objective 1
  - Objective 2
difficulty: "varies"
---
```

## Examples

### Example 1: Circuit Breaker Pattern

```yaml
---
title: "Circuit Breaker Pattern"
description: "Prevent cascade failures in distributed systems by failing fast when services are unhealthy"
date: 2024-01-15
modified: 2024-01-20
category: "patterns"
pattern_type: "resilience"
problem_solved: "Cascade failures from unhealthy dependencies"
when_to_use: "External service calls, microservice communication"
when_not_to_use: "Internal method calls, non-network operations"
tags:
  - resilience
  - fault-tolerance
  - circuit-breaker
  - design-patterns
difficulty: "intermediate"
reading_time: "15 min"
prerequisites:
  - /part1-axioms/axiom3-failure/
  - /patterns/timeout/
related:
  - /patterns/retry-backoff/
  - /patterns/bulkhead/
  - /case-studies/#netflix-hystrix
toc: true
weight: 10
---
```

### Example 2: Latency Axiom

```yaml
---
title: "Axiom 1: The Speed of Light is Not Infinite"
description: "Understanding how physics creates fundamental latency constraints in distributed systems"
date: 2024-01-10
category: "axioms"
axiom_number: 1
axiom_name: "Latency"
key_principle: "Information cannot travel faster than light, creating minimum latency bounds"
tags:
  - fundamental-constraints
  - latency
  - physics
  - networking
difficulty: "beginner"
reading_time: "20 min"
related:
  - /patterns/caching-strategies/
  - /patterns/edge-computing/
  - /quantitative/latency-calculations/
toc: true
weight: 1
---
```

## Migration Guide

To add frontmatter to existing files:

1. Add the frontmatter block at the very beginning of the file
2. Ensure the first line is `---`
3. Fill in at least the required fields
4. End with `---` on its own line
5. Leave a blank line before the content begins

## Validation

A validation script can check:
- Required fields are present
- Categories match expected values
- Links in prerequisites/related exist
- Dates are valid format
- Tags follow naming conventions

```python
# Example validation snippet
import yaml
import os

def validate_frontmatter(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    if not content.startswith('---'):
        return False, "No frontmatter found"
    
    # Extract frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False, "Invalid frontmatter format"
    
    try:
        fm = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        return False, f"YAML parse error: {e}"
    
    # Check required fields
    required = ['title', 'description', 'category', 'difficulty']
    missing = [f for f in required if f not in fm]
    
    if missing:
        return False, f"Missing required fields: {missing}"
    
    return True, "Valid"
```

---

*Consistent frontmatter enables better navigation, search, and content management across the Compendium.*