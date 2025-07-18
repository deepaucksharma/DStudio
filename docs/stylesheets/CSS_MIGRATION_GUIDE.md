# CSS Architecture Migration Guide

## Overview

This document outlines the migration from the old fragmented CSS architecture to the new modular system.

## Old Architecture Issues

1. **Multiple overlapping CSS files** (10+ files)
2. **2,895 lines in extra.css alone** with mixed concerns
3. **476 instances of !important** causing specificity wars
4. **Inline styles** scattered throughout markdown files
5. **Font size issues**: Hero subtitle at 30px, statistics at 60px
6. **Sub-pixel rendering issues** (elements at 664.5px)
7. **Inconsistent spacing and typography scale**

## New Architecture

### File Structure

```
stylesheets/
├── main.css                        # Entry point
└── new-architecture/
    ├── 00-design-tokens.css       # CSS variables & design system
    ├── 01-reset.css               # Modern CSS reset
    ├── 02-typography.css          # Typography system
    ├── 03-layout.css              # Layout utilities
    ├── 04-components.css          # UI components
    ├── 05-pages.css              # Page-specific styles
    ├── 06-utilities.css           # Utility classes
    └── 07-overrides.css          # MkDocs Material overrides
```

### Key Improvements

1. **Design Tokens System**
   - Consistent spacing scale (8px base)
   - Fluid typography with clamp()
   - Proper color palette with semantic naming
   - Standardized shadows and transitions

2. **Typography Fixes**
   - Hero subtitle: 30px → var(--font-size-xl) (clamp(1.25rem, 1.2rem + 0.25vw, 1.5rem))
   - Statistics: 60px → var(--font-size-3xl) (clamp(1.75rem, 1.5rem + 1.25vw, 2.25rem))
   - Consistent line heights and font weights

3. **Component Classes**
   - `.hero`, `.hero__title`, `.hero__subtitle`
   - `.stat`, `.stat__number`, `.stat__label`
   - `.axiom-box`, `.decision-box`, `.failure-vignette`, `.truth-box`
   - `.card`, `.btn`, `.badge`, `.nav-card`

4. **Utility Classes**
   - Spacing: `.m-*`, `.p-*`, `.gap-*`
   - Typography: `.text-*`, `.font-*`, `.leading-*`
   - Layout: `.grid`, `.flex`, `.hidden`
   - Colors: `.text-primary`, `.bg-neutral-*`

## Migration Steps

### 1. Update mkdocs.yml

Replace:
```yaml
extra_css:
  - stylesheets/extra.css
  - stylesheets/mobile.css
  - stylesheets/journey-map.css
  # ... etc
```

With:
```yaml
extra_css:
  - stylesheets/main.css
```

### 2. Replace Inline Styles

Old:
```html
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
```

New:
```html
<div class="grid grid--auto">
```

### 3. Update Component Markup

Old:
```html
<h4 style="color: var(--primary-color); margin: 0;">⚡ Latency</h4>
<p style="margin: 0.5rem 0; font-size: 0.9rem;">Speed of light...</p>
```

New:
```html
<div class="axiom-item">
  <h4 class="axiom-item__icon">⚡</h4>
  <div class="axiom-item__title">Latency</div>
  <p class="axiom-item__description">Speed of light...</p>
</div>
```

## Benefits

1. **Maintainability**: Clear separation of concerns
2. **Performance**: Reduced CSS file size, no conflicts
3. **Consistency**: Design tokens ensure uniform styling
4. **Scalability**: Easy to add new components
5. **Dark Mode**: Proper support with CSS variables
6. **Accessibility**: Better semantic HTML, proper contrast ratios

## Next Steps

1. Remove old CSS files after testing
2. Audit JavaScript files for hardcoded styles
3. Consider CSS preprocessing (SASS/LESS) for additional features
4. Implement CSS minification in build process

## Notes

- The new system uses CSS custom properties extensively
- All spacing follows an 8px grid system
- Typography uses fluid sizing for better responsiveness
- Dark mode is handled through CSS variables, not separate files