---
title: Full-Width Responsive Layouts with Material for MkDocs
description: Implementation guide for professional responsive design using Material theme features
---

# Full-Width Responsive Layouts with Material for MkDocs

This guide demonstrates how to implement full-width responsive layouts using Material for MkDocs built-in features, optimizing for all device sizes from mobile to ultra-wide displays.

## 1. Theme Configuration for Full Width

### Basic Full-Width Setup

Configure your `mkdocs.yml` to enable full-width layouts:

```yaml
theme:
 name: material
 features:
 - navigation.instant
 - navigation.tabs
 - navigation.sections
 - navigation.expand
 - toc.integrate
 - content.tabs.link
```

### Custom CSS for Full Width

Create `docs/stylesheets/extra.css`:

```css
/* Full-width configuration */
.md-grid {
 max-width: initial;
}

.md-content {
 max-width: none;
}

/* Constrain text for readability */
.md-typeset > :not(.grid):not(table):not(.tabbed-set) {
 max-width: 80ch;
 margin-left: auto;
 margin-right: auto;
}
```

Reference in `mkdocs.yml`:

```yaml
extra_css:
 - stylesheets/extra.css
```

## 2. Material's Grid System

### Enabling Grids

```yaml
markdown_extensions:
 - attr_list
 - md_in_html
```

### Grid Types & Patterns

#### Card Grid (Recommended for Navigation)

<div class="grid cards" markdown>

- :material-rocket-launch:{ .lg } **Getting Started**
 
 ---
 
 Quick introduction to distributed systems fundamentals
 
 [:octicons-arrow-right-24: Start here](../introduction/getting-started.md)

- :material-book-open-variant:{ .lg } **Core Concepts**
 
 ---
 
 7 Laws and 5 Pillars that govern all distributed systems
 
 [:octicons-arrow-right-24: Learn more](../axioms/index.md)

- :material-puzzle:{ .lg } **Design Patterns**
 
 ---
 
 50+ battle-tested patterns for common problems
 
 [:octicons-arrow-right-24: Browse patterns](../patterns/index.md)

- :material-chart-line:{ .lg } **Quantitative Tools**
 
 ---
 
 Mathematical models and calculators
 
 [:octicons-arrow-right-24: Explore tools](../quantitative/index.md)

</div>

#### Generic Grid (For Mixed Content)

<div class="grid" markdown>

!!! info "Information"
 Flexible grid item with admonition

```python
# Code block in grid
def distributed_system():
 return "scalable"
```

<div class="responsive-table" markdown>

| Metric | Value |
|--------|-------|
| Latency | 10ms |
| Throughput | 1M RPS |

</div>


</div>

## 3. Responsive Breakpoint Patterns

### Mobile-First Grid Configuration

```css
/* Base: Mobile (< 600px) */
.md-typeset .grid {
 display: grid;
 grid-template-columns: 1fr;
 gap: 1rem;
}

/* Tablet (600px - 1200px) */
@media screen and (min-width: 37.5em) {
 .md-typeset .grid {
 grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
 }
}

/* Desktop (1200px - 1920px) */
@media screen and (min-width: 75em) {
 .md-typeset .grid {
 grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
 gap: 1.5rem;
 }
}

/* Ultra-wide (> 1920px) */
@media screen and (min-width: 120em) {
 .md-typeset .grid {
 grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
 gap: 2rem;
 }
}
```

### Content Density Patterns

#### High-Density Dashboard Layout

<div class="grid cards" markdown>

- **Metric A** · `99.9%`
- **Metric B** · `42ms`
- **Metric C** · `1.2M`
- **Metric D** · `847GB`
- **Metric E** · `23.5k`
- **Metric F** · `99.99%`

</div>

#### Medium-Density Feature Grid

<div class="grid cards" markdown>

- :material-shield-check:{ .lg } **Security**
 
 End-to-end encryption, zero-trust architecture

- :material-lightning-bolt:{ .lg } **Performance**
 
 Sub-millisecond latency, linear scaling

- :material-cloud-sync:{ .lg } **Reliability**
 
 99.999% uptime, automatic failover

</div>

## 4. Responsive Tables

### Basic Responsive Table

```markdown
| Pattern | Mobile | Tablet | Desktop | Ultra-wide |
|---------|--------|--------|---------|------------|
| Columns | 1 | 2-3 | 3-4 | 5-6 |
| Font | 14px | 16px | 16px | 18px |
| Padding | 8px | 12px | 16px | 20px |
| Images | Hidden | Small | Medium | Large |

```

### Scrollable Table Wrapper

```html
<div class="responsive-table" markdown>

| Very | Wide | Table | With | Many | Columns | That | Scrolls | Horizontally |
|------|------|-------|------|------|---------|------|---------|--------------|
| Data | Data | Data | Data | Data | Data | Data | Data | Data |


</div>
```

```css
.table-wrapper {
 overflow-x: auto;
 -webkit-overflow-scrolling: touch;
}
```

## 5. Responsive Code Blocks

### Configure Line Wrapping

```yaml
markdown_extensions:
 - pymdownx.highlight:
 linenums: true
 linenums_style: pymdownx-inline
```

### Responsive Code Display

```css
/* Responsive code blocks */
.md-typeset pre {
 overflow-x: auto;
 max-width: 100%;
}

/* Mobile: Smaller font */
@media screen and (max-width: 37.5em) {
 .md-typeset code {
 font-size: 0.75rem;
 }
}
```

## 6. Professional Layout Patterns

### Hero Section with Full Width

```html
# Welcome to Distributed Systems

<div class="grid cards" markdown>

- **7** Fundamental Laws
- **5** Core Pillars 
- **50+** Design Patterns
- **20+** Case Studies

</div>
```

### Feature Comparison Grid

<div class="grid" markdown>

<div class="responsive-table" markdown>

| | **Option A** | **Option B** | **Option C** |
|---|:---:|:---:|:---:|
| **Performance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Scalability** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Cost** | $$$ | $ | $$ |
| **Complexity** | High | Low | Medium |

</div>


</div>

### Multi-Column Content Layout

```html
<div class="grid" markdown>

<div markdown>

### Column 1
Dense content optimized for scanning. Bullet points and structured data work best.

- Point 1
- Point 2
- Point 3

</div>

<div markdown>

### Column 2
Supporting information with details. Can include code snippets and examples.

```python
def example():
 return True
```

</div>

</div>
```

## 7. Mobile Optimization Patterns

### Progressive Enhancement

```css
/* Mobile-first approach */
.feature-grid {
 display: grid;
 gap: 1rem;
 grid-template-columns: 1fr;
}

/* Tablet: 2 columns */
@media (min-width: 768px) {
 .feature-grid {
 grid-template-columns: repeat(2, 1fr);
 }
}

/* Desktop: 3 columns */
@media (min-width: 1024px) {
 .feature-grid {
 grid-template-columns: repeat(3, 1fr);
 }
}

/* Ultra-wide: 4+ columns */
@media (min-width: 1920px) {
 .feature-grid {
 grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
 }
}
```

### Touch-Friendly Elements

```css
/* Larger touch targets on mobile */
@media (max-width: 768px) {
 .md-typeset .md-button {
 min-height: 48px;
 padding: 12px 24px;
 }
 
 .grid.cards .card {
 min-height: 60px;
 padding: 16px;
 }
}
```

## 8. Best Practices

### Do's

1. **Use Material's built-in grid system** - It's already responsive
2. **Test on real devices** - Chrome DevTools isn't enough
3. **Optimize images** - Use responsive images with srcset
4. **Minimize custom CSS** - Leverage Material's features first
5. **Use semantic HTML** - Better accessibility and SEO

### Don'ts

1. **Don't use fixed widths** - Use relative units (%, rem, vw)
2. **Don't hide essential content** - Progressive enhancement instead
3. **Don't nest grids unnecessarily** - Keep layouts simple
4. **Don't forget touch targets** - Minimum 48x48px on mobile
5. **Don't ignore performance** - Test on slow connections

## 9. Performance Considerations

### Optimize Grid Rendering

```css
/* Use CSS Grid's auto-fit for performance */
.md-typeset .grid {
 display: grid;
 grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr));
}

/* Avoid layout shifts */
.grid.cards .card {
 aspect-ratio: 16 / 9;
}
```

### Lazy Loading for Images

```markdown
![Description](image.jpg){ loading=lazy }
```

## 10. Example: Complete Responsive Page

```markdown
---
title: Responsive Dashboard
hide:
 - navigation
 - toc
---

# System Dashboard

<div class="grid cards" markdown>

- :material-server:{ .lg } **Servers**
 
 ---
 
 **Status:** ✅ All systems operational
 
 - Region 1: `99.9%` uptime
 - Region 2: `99.8%` uptime
 - Region 3: `99.9%` uptime

- :material-chart-line:{ .lg } **Performance**
 
 ---
 
 **Current Metrics:**
 
<div class="responsive-table" markdown>

 | Metric | Value | Trend |
 |--------|-------|-------|
 | Latency | 12ms | ↓ 5% |
 | RPS | 1.2M | ↑ 10% |
 | Errors | 0.01% | → 0% |

</div>


- :material-database:{ .lg } **Database**
 
 ---
 
 **Cluster Health:**
 
 - Primary: `Active`
 - Replica 1: `Synced`
 - Replica 2: `Synced`
 - Storage: `42%` used

</div>

## Detailed Metrics

<div class="grid" markdown>

!!! success "API Gateway"
 - Requests: `847M` today
 - Avg response: `23ms`
 - Cache hit rate: `94%`

!!! info "Message Queue"
 - Messages: `12.3M` pending
 - Processing: `84K/sec`
 - Lag: `< 1 sec`

!!! warning "Storage"
 - Used: `8.4TB / 20TB`
 - Growth: `+120GB/day`
 - Cleanup scheduled

</div>
```

## Summary

Material for MkDocs provides excellent built-in responsive features. Focus on:

1. **Use Material's grid system** with `attr_list` and `md_in_html`
2. **Configure full-width** via custom CSS on `.md-grid`
3. **Leverage card grids** for navigation and feature showcases
4. **Apply mobile-first** responsive breakpoints
5. **Test thoroughly** across all device sizes

The key is to work *with* Material's features rather than against them, using minimal custom CSS only where necessary.