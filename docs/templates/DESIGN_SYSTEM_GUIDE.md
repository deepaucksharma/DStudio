# DStudio Design System Guide

This guide explains the minimal design system implemented to fix UI/UX issues while maintaining simplicity.

## Overview of Changes

### 1. Design System CSS (`design-system.css`)
- **Typography Scale**: Consistent font sizes from `xs` to `4xl`
- **Spacing System**: 8px-based scale for consistent spacing
- **Color Palette**: Simplified colors with proper contrast
- **Components**: Card layouts, buttons, and content boxes
- **Dark Mode**: Full support with appropriate color adjustments

### 2. Style Overrides (`overrides.css`)
- Removes excessive emojis from navigation and content
- Fixes mobile navigation issues
- Improves table responsiveness
- Standardizes component styling

### 3. MkDocs Configuration Updates
- Added navigation features for better UX
- Enabled breadcrumbs and back-to-top button
- Improved mobile navigation collapse

## Component Usage

### Cards
Use for organizing related content in a grid:

```markdown
<div class="grid" markdown>
  <div class="card">
    <h3 class="card__title">Title</h3>
    <p class="card__description">Description</p>
  </div>
</div>
```

### Content Boxes
Four types available:

```markdown
<div class="content-box axiom-box">
  <h3>Axiom/Principle</h3>
  <p>Fundamental truth or principle</p>
</div>

<div class="content-box decision-box">
  <h3>Decision Guide</h3>
  <p>When to use vs not use</p>
</div>

<div class="content-box failure-vignette">
  <h3>Failure Story</h3>
  <p>What went wrong and lessons learned</p>
</div>

<div class="content-box truth-box">
  <h3>Key Insight</h3>
  <p>Important takeaway or insight</p>
</div>
```

### Tables
Use responsive tables for better mobile experience:

```markdown
<table class="responsive-table">
<thead>
  <tr>
    <th>Column 1</th>
    <th>Column 2</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td data-label="Column 1">Value 1</td>
    <td data-label="Column 2">Value 2</td>
  </tr>
</tbody>
</table>
```

## Best Practices

### 1. Typography
- Use proper heading hierarchy (h1 → h2 → h3)
- Keep paragraphs concise
- Max line length of ~80 characters for readability

### 2. Emojis
- **Removed** from navigation and headings
- **Minimal use** in content only when necessary
- **No emoji bullets** in lists

### 3. Navigation
- Clear, descriptive labels
- Logical grouping of content
- Breadcrumbs help orientation

### 4. Mobile First
- All components are responsive
- Touch targets are 44x44px minimum
- Tables transform on small screens

### 5. Accessibility
- Proper color contrast (WCAG AA)
- Focus indicators for keyboard navigation
- Semantic HTML structure
- Screen reader friendly

## Templates Available

### 1. Pattern Template (`pattern-template.md`)
- Consistent structure for design patterns
- Problem-solution format
- Trade-off tables
- Related patterns section

### 2. Law Template (`law-template.md`)
- Physics-based derivation
- Mathematical proofs
- System implications
- Failure scenarios

### 3. Case Study Template (`case-study-template.md`)
- System overview with metrics
- Architecture diagrams
- Law mapping analysis
- Lessons learned

### 4. Homepage Template (`homepage-template.md`)
- Clean hero section
- Feature cards
- Learning paths
- Quick stats

## Implementation Checklist

When updating content:

- [ ] Remove emoji bullets from lists
- [ ] Remove emojis from headings
- [ ] Use content boxes for callouts
- [ ] Implement responsive tables
- [ ] Add proper spacing between sections
- [ ] Use card grids for related items
- [ ] Ensure mobile responsiveness
- [ ] Check color contrast
- [ ] Test keyboard navigation
- [ ] Verify dark mode appearance

## Color Palette Reference

### Light Mode
- Primary: `#5448C8` (Indigo)
- Accent: `#00BCD4` (Cyan)
- Success: `#10B981` (Green)
- Warning: `#F59E0B` (Amber)
- Error: `#EF4444` (Red)
- Info: `#3B82F6` (Blue)

### Neutral Colors
- Gray 50-900 scale for backgrounds and text
- Automatic adjustments for dark mode

## Spacing Scale

Use consistent spacing:
- `xs`: 4px
- `sm`: 8px
- `md`: 16px
- `lg`: 24px
- `xl`: 32px
- `2xl`: 48px
- `3xl`: 64px

## Next Steps

1. Apply templates to existing content gradually
2. Remove emojis from navigation items
3. Update tables to use responsive classes
4. Convert long lists to card grids where appropriate
5. Test on various devices and screen sizes

The goal is a clean, professional, and accessible documentation site that works well on all devices without unnecessary visual clutter.