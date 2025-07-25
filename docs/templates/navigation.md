# Navigation Enhancement Templates

This document provides templates and best practices for implementing comprehensive navigation on every page of the documentation.

## Page Front Matter Template

Every page should include navigation metadata in its front matter:

```yaml
---
# Basic page info
title: "Your Page Title"
description: "Brief description for SEO and previews"

# Navigation metadata
nav:
 # Learning path this page belongs to
 learning_path: "senior-engineer" # Options: new-graduate, senior-engineer, manager, architect
 
 # Position in sequence
 sequence:
 current: 3
 total: 8
 
 # Related content
 related:
 - title: "Related Pattern"
 path: "/patterns/circuit-breaker/"
 type: "pattern"
 - title: "Case Study Example"
 path: "/case-studies/netflix-chaos/"
 type: "case-study"
 
 # Prerequisites
 prerequisites:
 - title: "Understanding CAP Theorem"
 path: "/quantitative/cap-theorem/"
 - title: "Distributed State Basics"
 path: "/part2-pillars/state/"
 
 # Next steps
 next_steps:
 - title: "Implement Circuit Breaker"
 path: "/patterns/circuit-breaker/"
 level: "beginner"
 - title: "Advanced Retry Strategies"
 path: "/patterns/retry-backoff/"
 level: "intermediate"
 
 # Tags for categorization
 tags:
 - reliability
 - patterns
 - intermediate
---
```

## Navigation Components

### 1. Page Header Navigation

Add this at the top of each page:

```markdown
{% if page.meta.nav %}
<!-- Learning Path Indicator -->
<div class="learning-path-indicator">
 <span class="path-label">Learning Path:</span>
 <span class="path-name">{{ page.meta.nav.learning_path | title }}</span>
 {% if page.meta.nav.sequence %}
 <span class="sequence">Part {{ page.meta.nav.sequence.current }} of {{ page.meta.nav.sequence.total }}</span>
 {% endif %}
</div>
{% endif %}

<!-- Breadcrumb Enhancement -->
<nav class="enhanced-breadcrumb" aria-label="Breadcrumb">
 <ol>
 <li><a href="/">Home</a></li>
 <li><a href="../">{{ page.parent.title }}</a></li>
 <li aria-current="page">{{ page.title }}</li>
 </ol>
</nav>
```

### 2. Prerequisites Section

Place after the page introduction:

```markdown
{% if page.meta.nav.prerequisites %}
!!! info "Prerequisites"
 Before diving into this topic, make sure you understand:
 
 {% for prereq in page.meta.nav.prerequisites %}
 - [{{ prereq.title }}]({{ prereq.path }})
 {% endfor %}
{% endif %}
```

### 3. In-Page Navigation Helper

For long pages, add a floating navigation helper:

```markdown
<div class="nav-title">On This Page
 <nav class="quick-nav">
 <a href="#section1" class="nav-item">Introduction</a>
 <a href="#section2" class="nav-item">Core Concepts</a>
 <a href="#section3" class="nav-item">Implementation</a>
 <a href="#section4" class="nav-item">Best Practices</a>
 </nav>
 <button class="nav-btn" onclick="window.scrollTo(0,0)">↑ Top</button>
 <button class="nav-btn" onclick="window.print()">🖨️ Print</button>
</div>
```

### 4. Related Content Section

Add at the bottom of the page, before the footer:

```markdown
{% if page.meta.nav.related %}
## 🔗 Related Content

{% for item in page.meta.nav.related %}
 <div class="related-card" data-type="{{ item.type }}">
 <div class="card-type">{{ item.type | replace("_", " ") | title }}
 <h4><a href="{{ item.path }}">{{ item.title }}</a></h4>
 </div>
{% endfor %}
</div>
{% endif %}
```

### 5. Next Steps Section

```markdown
{% if page.meta.nav.next_steps %}
## 🚀 What's Next?

{% for step in page.meta.nav.next_steps %}
 <div class="step-card level-{{ step.level }}">
 <span class="level-badge">{{ step.level | title }}</span>
 <h4><a href="{{ step.path }}">{{ step.title }}</a></h4>
{% endfor %}
</div>
{% endif %}
```

### 6. Progress Indicator

For multi-part series:

```markdown
{% if page.meta.nav.sequence %}
<div class="progress-bar">
 <div class="progress-fill">
 </div>
 Progress: {{ page.meta.nav.sequence.current }} of {{ page.meta.nav.sequence.total }} completed
</div>
{% endif %}
```

## Implementation Examples

### Example 1: Pattern Page

```yaml
---
title: "Circuit Breaker Pattern"
description: "Prevent cascading failures with the Circuit Breaker pattern"

nav:
 learning_path: "senior-engineer"
 
 sequence:
 current: 3
 total: 10
 
 prerequisites:
 - title: "Failure Modes"
 path: "/part1-axioms/law1-failure/"
 - title: "State Management"
 path: "/part2-pillars/state/"
 
 related:
 - title: "Retry Pattern"
 path: "/patterns/retry-backoff/"
 type: "pattern"
 - title: "Netflix Chaos Engineering"
 path: "/case-studies/netflix-chaos/"
 type: "case-study"
 - title: "Timeout Pattern"
 path: "/patterns/timeout/"
 type: "pattern"
 
 next_steps:
 - title: "Implement Basic Circuit Breaker"
 path: "/tutorials/circuit-breaker-basic/"
 level: "beginner"
 - title: "Advanced Circuit Breaker"
 path: "/tutorials/circuit-breaker-advanced/"
 level: "intermediate"
 
 tags:
 - reliability
 - fault-tolerance
 - pattern
---
```

### Example 2: Case Study Page

```yaml
---
title: "Netflix Streaming Architecture"
description: "Deep dive into Netflix's globally distributed streaming platform"

nav:
 learning_path: "architect"
 
 prerequisites:
 - title: "CDN Basics"
 path: "/patterns/cdn/"
 - title: "Video Streaming Fundamentals"
 path: "/case-studies/video-streaming/"
 
 related:
 - title: "Edge Computing"
 path: "/patterns/edge-computing/"
 type: "pattern"
 - title: "Multi-Region Architecture"
 path: "/patterns/multi-region/"
 type: "pattern"
 - title: "Chaos Engineering"
 path: "/human-factors/chaos-engineering/"
 type: "practice"
 
 next_steps:
 - title: "Design Your Own CDN"
 path: "/exercises/design-cdn/"
 level: "advanced"
 
 tags:
 - streaming
 - scale
 - case-study
 - netflix
---
```

## Navigation Macros

Create reusable navigation components:

```python
# In docs/macros/__init__.py

def define_env(env):
 """Define navigation helper macros"""
 
 @env.macro
 def nav_prerequisites(prereqs):
 """Generate prerequisites section"""
 if not prereqs:
 return ""
 
 html = ['!!! info
 ']
 html.append('<h4>📚 Before You Begin</h4>')
 html.append('<ul>')
 
 for prereq in prereqs:
 html.append(f'<li><a href="{prereq["path"]}">{prereq["title"]}</a></li>')
 
 html.append('</ul>')
 html.append('')
 
 return '\n'.join(html)
 
 @env.macro
 def nav_learning_path(path_name, current=None, total=None):
 """Generate learning path indicator"""
 html = ['']
 html.append(f'<span class="path-icon">🎯</span>')
 html.append(f'<span class="path-name">{path_name}</span>')
 
 if current and total:
 progress = (current / total) * 100
 html.append(f'<span class="path-progress">{current}/{total}</span>')
 html.append(f'<div class="mini-progress">')
 
 html.append('</div>')
 return '\n'.join(html)
 
 @env.macro
 def nav_related_grid(related_items):
 """Generate related content grid"""
 if not related_items:
 return ""
 
 html = ['']
 html.append('<h3>🔗 Related Resources</h3>')
 html.append('<div class="related-grid">')
 
 for item in related_items:
 icon = {
 'pattern': '🔧',
 'case-study': '📊',
 'tutorial': '📖',
 'theory': '📐'
 }.get(item.get('type', ''), '📄')
 
 html.append(f'<a href="{item["path"]}" class="related-item">')
 html.append(f'<span class="item-icon">{icon}</span>')
 html.append(f'<span class="item-title">{item["title"]}</span>')
 html.append(f'<span class="item-type">{item.get("type", "")}</span>')
 html.append('</a>')
 
 html.append('')
 html.append('</div>')
 
 return '\n'.join(html)
```

## Usage in Pages

```markdown
---
title: "Your Page Title"
# ... navigation metadata ...
---

# {{ page.title }}

{{ nav_learning_path(page.meta.nav.learning_path, page.meta.nav.sequence.current, page.meta.nav.sequence.total) }}

{{ nav_prerequisites(page.meta.nav.prerequisites) }}

<!-- Your content here -->

{{ nav_related_grid(page.meta.nav.related) }}
```

## Best Practices

1. **Always include navigation metadata** in front matter
2. **Use consistent categorization** for learning paths
3. **Limit related items** to 3-5 most relevant
4. **Order prerequisites** from most to least important
5. **Tag appropriately** for better discoverability
6. **Test navigation flow** by following the paths
7. **Update related links** when adding new content

## Navigation Types by Page Type

| Page Type | Required Navigation | Optional Navigation |
|-----------|-------------------|-------------------|
| **Pattern** | Prerequisites, Related Patterns | Case Studies, Next Steps |
| **Case Study** | Related Patterns, Key Concepts | Prerequisites, Similar Cases |
| **Theory/Law** | Examples, Exercises | Prerequisites, Applications |
| **Tutorial** | Prerequisites, Next Steps | Related Patterns, Case Studies |
| **Reference** | Related Topics | Examples, Tutorials |