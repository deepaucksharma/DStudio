---
title: MkDocs Responsive Configuration Guide
description: Complete configuration for full-width responsive layouts
---

# MkDocs Responsive Configuration Guide

Complete configuration examples for implementing professional full-width responsive layouts using Material for MkDocs.

## 1. Minimal Full-Width Configuration

### mkdocs.yml

```yaml
site_name: My Documentation
theme:
 name: material
 
# Enable grids and responsive features
markdown_extensions:
 - attr_list
 - md_in_html
 - tables
 - admonition
 - pymdownx.details
 - pymdownx.superfences
 - pymdownx.tabbed:
 alternate_style: true

# Custom CSS for full width
extra_css:
 - stylesheets/extra.css
```

### stylesheets/extra.css

```css
/* Remove max-width constraints */
.md-grid {
 max-width: initial;
}

/* Responsive grid system */
.md-typeset .grid {
 display: grid;
 gap: 1rem;
 grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr));
}

/* Maintain readable line length for text */
.md-typeset > p,
.md-typeset > ul,
.md-typeset > ol {
 max-width: 80ch;
 margin-left: auto;
 margin-right: auto;
}
```

## 2. Advanced Responsive Configuration

### Complete mkdocs.yml

```yaml
site_name: Distributed Systems Compendium
site_url: https://example.com/
site_description: Learn distributed systems from first principles

theme:
 name: material
 
 # Responsive navigation features
 features:
 # Navigation
 - navigation.instant # Instant loading
 - navigation.instant.prefetch # Prefetch pages
 - navigation.tracking # Update URL on scroll
 - navigation.tabs # Top-level tabs
 - navigation.tabs.sticky # Sticky tabs
 - navigation.sections # Collapsible sections
 - navigation.expand # Expand all sections
 - navigation.indexes # Section index pages
 - navigation.top # Back to top button
 
 # Table of Contents
 - toc.follow # Follow scroll
 - toc.integrate # Integrate with navigation
 
 # Search
 - search.suggest # Search suggestions
 - search.highlight # Highlight results
 
 # Content
 - content.tabs.link # Link content tabs
 - header.autohide # Hide header on scroll

 # Color scheme
 palette:
 - media: "(prefers-color-scheme: light)"
 scheme: default
 primary: indigo
 accent: amber
 toggle:
 icon: material/brightness-7
 name: Switch to dark mode
 - media: "(prefers-color-scheme: dark)"
 scheme: slate
 primary: indigo
 accent: amber
 toggle:
 icon: material/brightness-4
 name: Switch to light mode

 # Typography
 font:
 text: Inter # Or Roboto, Open Sans
 code: Fira Code # Or JetBrains Mono

# Plugins for enhanced functionality
plugins:
 - search:
 separator: '[\s\-,:!=\[\]()"`/]+|\.(?!\d)|&[lg]t;|(?!\b)(?=[A-Z][a-z])'
 - minify:
 minify_html: true

# Full extension set for responsive content
markdown_extensions:
 # Essential for responsive layouts
 - attr_list
 - md_in_html
 - tables
 
 # Content enhancements
 - admonition
 - footnotes
 - meta
 - toc:
 permalink: true
 toc_depth: 3
 
 # Code blocks
 - pymdownx.highlight:
 anchor_linenums: true
 line_spans: __span
 pygments_lang_class: true
 - pymdownx.inlinehilite
 - pymdownx.snippets
 - pymdownx.superfences:
 custom_fences:
 - name: mermaid
 class: mermaid
 format: !!python/name:pymdownx.superfences.fence_code_format
 
 # UI elements
 - pymdownx.details
 - pymdownx.tabbed:
 alternate_style: true
 - pymdownx.tasklist:
 custom_checkbox: true
 - pymdownx.keys
 - pymdownx.smartsymbols
 
 # Rich content
 - pymdownx.emoji:
 emoji_index: !!python/name:material.extensions.emoji.twemoji
 emoji_generator: !!python/name:material.extensions.emoji.to_svg

# Custom CSS
extra_css:
 - stylesheets/responsive.css

# Custom JavaScript (optional)
extra_javascript:
 - javascripts/responsive.js
```

## 3. Comprehensive Responsive CSS

### stylesheets/responsive.css

```css
/* ================================================
 FULL-WIDTH RESPONSIVE LAYOUT SYSTEM
 Mobile-first approach with progressive enhancement
 ================================================ */

/* === BASE: FULL-WIDTH CONFIGURATION === */
.md-grid,
.md-main__inner,
.md-content__inner {
 max-width: initial;
}

/* === RESPONSIVE GRID SYSTEM === */
/* Default: Single column mobile */
.md-typeset .grid {
 display: grid;
 gap: 1rem;
 grid-template-columns: 1fr;
}

/* Small tablets (600px+) */
@media screen and (min-width: 37.5em) {
 .md-typeset .grid {
 grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
 gap: 1.25rem;
 }
}

/* Large tablets/small laptops (960px+) */
@media screen and (min-width: 60em) {
 .md-typeset .grid {
 grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
 gap: 1.5rem;
 }
}

/* Desktop (1280px+) */
@media screen and (min-width: 80em) {
 .md-typeset .grid {
 grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
 gap: 2rem;
 }
}

/* Ultra-wide (1920px+) */
@media screen and (min-width: 120em) {
 .md-typeset .grid {
 grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
 gap: 2.5rem;
 }
 
 /* Wider sidebars for large screens */
 .md-sidebar--primary {
 width: 300px;
 }
 
 .md-sidebar--secondary {
 width: 240px;
 }
}

/* === CONTENT WIDTH OPTIMIZATION === */
/* Constrain text for readability */
.md-typeset > :is(p, ul, ol, blockquote) {
 max-width: 80ch;
 margin-left: auto;
 margin-right: auto;
}

/* Full-width elements */
.md-typeset :is(.grid, table, .tabbed-set, .highlight, .admonition, .details) {
 max-width: none;
}

/* === RESPONSIVE TABLES === */
/* Wrapper for horizontal scroll */
.table-responsive {
 overflow-x: auto;
 -webkit-overflow-scrolling: touch;
 margin: 1rem 0;
}

/* Responsive table styling */
@media screen and (max-width: 60em) {
 .md-typeset table {
 font-size: 0.875rem;
 }
 
 .md-typeset table th,
 .md-typeset table td {
 padding: 0.5rem;
 }
}

/* === RESPONSIVE NAVIGATION === */
/* Mobile navigation improvements */
@media screen and (max-width: 76.1875em) {
 /* Larger touch targets */
 .md-nav__link {
 padding: 0.75rem 1rem;
 }
 
 /* Better spacing for mobile */
 .md-nav__item {
 margin: 0.25rem 0;
 }
}

/* === RESPONSIVE CARDS === */
.md-typeset .grid.cards > * {
 background: var(--md-default-bg-color);
 border: 1px solid var(--md-default-fg-color--lightest);
 border-radius: 0.25rem;
 padding: 1rem;
 transition: all 0.3s;
}

.md-typeset .grid.cards > :hover {
 box-shadow: 0 4px 12px rgba(0,0,0,0.1);
 transform: translateY(-2px);
}

/* Mobile card adjustments */
@media screen and (max-width: 37.5em) {
 .md-typeset .grid.cards > * {
 padding: 0.75rem;
 }
}

/* === RESPONSIVE CODE BLOCKS === */
.md-typeset pre {
 overflow-x: auto;
 max-width: 100%;
}

/* Smaller code font on mobile */
@media screen and (max-width: 37.5em) {
 .md-typeset code {
 font-size: 0.75rem;
 }
}

/* === RESPONSIVE ADMONITIONS === */
@media screen and (max-width: 60em) {
 .md-typeset .admonition {
 margin: 1rem -0.5rem;
 border-radius: 0;
 }
}

/* === UTILITY CLASSES === */
/* Force full viewport width */
.full-viewport {
 width: 100vw;
 position: relative;
 left: 50%;
 right: 50%;
 margin-left: -50vw;
 margin-right: -50vw;
}

/* Container widths */
.container-sm { max-width: 640px; margin: 0 auto; }
.container-md { max-width: 768px; margin: 0 auto; }
.container-lg { max-width: 1024px; margin: 0 auto; }
.container-xl { max-width: 1280px; margin: 0 auto; }

/* Responsive spacing */
.py-responsive {
 padding-top: 1rem;
 padding-bottom: 1rem;
}

@media screen and (min-width: 60em) {
 .py-responsive {
 padding-top: 2rem;
 padding-bottom: 2rem;
 }
}

@media screen and (min-width: 80em) {
 .py-responsive {
 padding-top: 3rem;
 padding-bottom: 3rem;
 }
}

/* === PRINT STYLES === */
@media print {
 .md-typeset .grid {
 grid-template-columns: repeat(2, 1fr);
 gap: 0.5rem;
 }
 
 .md-sidebar,
 .md-header,
 .md-footer {
 display: none;
 }
 
 .md-content {
 margin: 0;
 max-width: 100%;
 }
}
```

## 4. JavaScript Enhancements (Optional)

### javascripts/responsive.js

```javascript
// Responsive table wrapper
document.addEventListener('DOMContentLoaded', function() {
 // Wrap tables for horizontal scroll
 const tables = document.querySelectorAll('.md-typeset table:not(.no-wrap)');
 tables.forEach(table => {
 if (!table.parentElement.classList.contains('table-responsive')) {
 const wrapper = document.createElement('div');
 wrapper.className = 'table-responsive';
 table.parentNode.insertBefore(wrapper, table);
 wrapper.appendChild(table);
 }
 });
 
 // Add responsive classes based on viewport
 function updateResponsiveClasses() {
 const width = window.innerWidth;
 document.body.classList.toggle('mobile', width < 600);
 document.body.classList.toggle('tablet', width >= 600 && width < 960);
 document.body.classList.toggle('desktop', width >= 960 && width < 1920);
 document.body.classList.toggle('ultra-wide', width >= 1920);
 }
 
 updateResponsiveClasses();
 window.addEventListener('resize', updateResponsiveClasses);
 
 // Responsive image loading
 if ('loading' in HTMLImageElement.prototype) {
 const images = document.querySelectorAll('img[loading="lazy"]');
 images.forEach(img => {
 img.src = img.dataset.src;
 });
 }
});
```

## 5. Content Patterns

### Grid Layouts

```markdown
<!-- Basic responsive grid -->
<div class="grid" markdown>

- Item 1
- Item 2 
- Item 3
- Item 4

</div>

<!-- Card grid with icons -->
<div class="grid cards" markdown>

- :material-rocket:{ .lg } **Title**
 
 ---
 
 Description here
 
 [Learn more](#)

- :material-book:{ .lg } **Title**
 
 ---
 
 Description here
 
 [Learn more](#)

</div>
```

### Responsive Tables

```markdown
<!-- Wrapped for mobile -->
<div class="responsive-table" markdown>

| Column 1 | Column 2 | Column 3 | Column 4 | Column 5 |
|----------|----------|----------|----------|----------|
| Data | Data | Data | Data | Data |


</div>
```

### Full-Width Sections

```markdown
<!-- Full viewport width -->
# Full Width Hero Section

<div class="container-lg grid" markdown>
<!-- Content constrained within -->

</div>
```

## 6. Testing Responsive Layouts

### Browser DevTools

1. **Chrome/Edge**: F12 → Toggle device toolbar
2. **Firefox**: F12 → Responsive Design Mode
3. **Safari**: Develop → Enter Responsive Design Mode

### Key Breakpoints to Test

- **320px**: Small mobile
- **375px**: iPhone SE/8
- **414px**: iPhone Plus/Max
- **768px**: iPad Portrait
- **1024px**: iPad Landscape
- **1280px**: Small laptop
- **1440px**: Desktop
- **1920px**: Full HD
- **2560px**: Ultra-wide

### Performance Metrics

- First Contentful Paint < 1.5s
- Largest Contentful Paint < 2.5s
- Cumulative Layout Shift < 0.1
- Time to Interactive < 3.5s

## Summary

This configuration provides:

1. **Full-width layouts** with constrained text for readability
2. **Responsive grids** that adapt from 1-6+ columns
3. **Mobile-optimized** navigation and touch targets
4. **Performance optimized** with lazy loading and minification
5. **Accessible** with semantic HTML and ARIA labels
6. **Print-friendly** with appropriate media queries

The key is using Material's built-in features with minimal custom CSS, ensuring maintainability and compatibility with future updates.