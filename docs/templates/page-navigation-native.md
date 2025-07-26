# Page Navigation Template - MkDocs Material Native

This template shows how to enhance pages using only MkDocs Material's built-in features.

## Front Matter Template

```yaml
---
title: "Page Title"
description: "SEO-friendly description"
icon: material/book  # Optional page icon
status: new  # Shows badge: new, deprecated, etc.
search:
  boost: 2  # Boost in search results (1-10)
  exclude: false  # Exclude from search
tags:
  - distributed-systems
  - pattern-name
  - difficulty-level
---
```

## Page Structure Template

```markdown
# Page Title

!!! abstract "Overview"
    Brief description of what this page covers. This appears prominently at the top.

## Prerequisites

!!! prerequisite "Before You Begin"
    
    Make sure you understand these fundamental concepts:
    
    - :material-book: [Concept 1](../path/to/concept1/) - Brief description
    - :material-book: [Concept 2](../path/to/concept2/) - Brief description
    - :material-book: [Concept 3](../path/to/concept3/) - Brief description

## Quick Info

**Difficulty:** :material-signal-cellular-2: Intermediate | 
**Reading Time:** :material-clock: 25 min |
**Category:** :material-folder: Patterns |
**Tags:** `consistency` `distributed-systems`

## Main Content

Content goes here...

## Related Topics

=== "Patterns"

    <div class="grid cards" markdown>
    
    - :material-puzzle:{ .lg .middle } __[Related Pattern 1](../patterns/pattern1/)__
    
        ---
        
        Brief description of how this pattern relates.
    
    - :material-puzzle:{ .lg .middle } __[Related Pattern 2](../patterns/pattern2/)__
    
        ---
        
        Brief description of how this pattern relates.
    
    </div>

=== "Case Studies"

    Real-world implementations:
    
    - **[Company X Case Study](../case-studies/company-x/)** - How they implemented this at scale
    - **[Company Y Case Study](../case-studies/company-y/)** - Lessons learned from production
    - **[Company Z Case Study](../case-studies/company-z/)** - Alternative approach

=== "Theory"

    Theoretical foundations:
    
    - **[Mathematical Model](../quantitative/model/)** - Formal analysis
    - **[Performance Analysis](../quantitative/performance/)** - Benchmarks and metrics
    - **[Trade-off Analysis](../quantitative/tradeoffs/)** - When to use vs alternatives

## Next Steps

!!! tip "Continue Your Learning"
    
    Based on your understanding of this topic, here are recommended next steps:
    
    **Beginner Path**
    : Start with hands-on tutorials to solidify understanding
    : - [Basic Implementation Tutorial](../tutorials/basic/)
    : - [Simple Examples](../examples/simple/)
    
    **Intermediate Path**
    : Explore advanced features and optimizations
    : - [Production Patterns](../tutorials/production/)
    : - [Performance Tuning](../tutorials/performance/)
    
    **Advanced Path**
    : Deep dive into complex scenarios
    : - [Edge Cases](../tutorials/edge-cases/)
    : - [Research Papers](../references/papers/)

## Key Takeaways

!!! success "Remember These Points"
    1. **Key Point 1** - Most important concept
    2. **Key Point 2** - Critical understanding
    3. **Key Point 3** - Common pitfall to avoid

## Additional Resources

??? info "References and Further Reading"
    
    **Papers:**
    - [Original Paper Title](https://link) - Author et al.
    - [Follow-up Research](https://link) - Author et al.
    
    **Books:**
    - Book Title by Author - Chapter X is particularly relevant
    
    **Online Resources:**
    - [Official Documentation](https://link)
    - [Community Tutorial](https://link)

---

<div class="page-nav" markdown>
[:material-arrow-left: Previous Topic](..#/) | 
[:material-arrow-up: Section Index](../index.md) | 
[:material-arrow-right: Next Topic](..#/)
</div>
```

## Using MkDocs Material Features

### 1. Admonitions for Different Purposes

```markdown
!!! note "Default Note"
    General information

!!! abstract "Summary/Overview"
    High-level summary

!!! info "Additional Information"
    Supplementary details

!!! tip "Best Practice"
    Helpful suggestions

!!! success "Key Point"
    Important takeaway

!!! question "Think About This"
    Reflection prompt

!!! warning "Common Pitfall"
    What to avoid

!!! failure "Anti-Pattern"
    What not to do

!!! danger "Critical Warning"
    Security or data loss risk

!!! bug "Known Issue"
    Current limitations

!!! example "Example Usage"
    Code or scenario example

!!! quote "Notable Quote"
    Relevant citation

!!! prerequisite "Prerequisites"
    Required knowledge (custom type)
```

### 2. Collapsible Content

```markdown
??? note "Click to expand"
    Hidden by default
    
???+ note "Expanded by default"
    Visible by default but can be collapsed
```

### 3. Content Tabs

```markdown
=== "Tab 1"

    Content for tab 1

=== "Tab 2"

    Content for tab 2

=== "Tab 3"

    Content for tab 3
```

### 4. Definition Lists

```markdown
Term 1
:   Definition for term 1

Term 2
:   Definition for term 2
    
    Can include multiple paragraphs
    
Term 3
:   Definition with code
    
    ```python
    example = "code"
    ```
```

### 5. Grid Cards

```markdown
<div class="grid cards" markdown>

- :material-clock-fast:{ .lg .middle } __Card Title 1__

    ---

    Card description with markdown support

    :octicons-arrow-right-24: Learn more

- :material-book:{ .lg .middle } __Card Title 2__

    ---

    Another card with different icon

    :octicons-arrow-right-24: Explore

</div>
```

### 6. Keyboard Keys

```markdown
Press ++ctrl+alt+del++ to restart
```

### 7. Task Lists

```markdown
- [x] Completed task
- [ ] Pending task
- [ ] Another pending task
```

### 8. Highlighting Changes

```markdown
Text with {~~deleted~>added~~} content
Text with {==highlighted==} content
Text with {^^inserted^^} content
Text with {~~deleted~~} content
```

### 9. Footnotes

```markdown
This needs a citation[^1].

[^1]: This is the footnote content.
```

### 10. Icons

```markdown
:material-account: User
:material-clock: Time
:material-home: Home
:fontawesome-brands-github: GitHub
:octicons-arrow-right-24: Arrow
```

## Navigation Patterns

### 1. Section Navigation

```markdown
## In This Section

- [Subtopic 1](#subtopic-1)
- [Subtopic 2](#subtopic-2)
- [Subtopic 3](#subtopic-3)
```

### 2. Breadcrumb-style Path

```markdown
[Home](/) > [Patterns](patterns) > [Current Page](patterns/current)
```

### 3. Previous/Next Navigation

```markdown
---

[:material-arrow-left: Previous: Topic Name](..#/) | 
[:material-arrow-up: Up: Section Name](../index.md) | 
[:material-arrow-right: Next: Topic Name](..#/)
```

### 4. See Also Section

```markdown
## See Also

- [Related Topic 1](../related1/) - How it connects
- [Related Topic 2](../related2/) - Why it's relevant
- [Related Topic 3](../related3/) - Additional context
```

## Search Optimization

### 1. Boost Important Pages

```yaml
---
search:
  boost: 2.0  # Higher number = higher in search results
---
```

### 2. Exclude from Search

```yaml
---
search:
  exclude: true
---
```

### 3. Use Descriptive Headings

Instead of generic headings, use specific ones that help with search:
- ❌ "Overview"
- ✅ "Circuit Breaker Pattern Overview"

## Benefits

1. **No Custom Code**: Pure MkDocs Material
2. **Maintainable**: Standard markdown
3. **Searchable**: All content properly indexed
4. **Accessible**: Works without JavaScript
5. **Fast**: No additional scripts
6. **Responsive**: Mobile-friendly by default
7. **Printable**: Clean print styles included

## Example Implementation

See the enhanced pages:
- `/docs/patterns/circuit-breaker-native.md`
- `/docs/case-studies/cassandra-native.md`
- `/docs/quantitative/cap-theorem-native.md`