# Layout & Grid System

## Layout Philosophy

### Core Principles
1. **Content-First Design**: Layout serves content, not vice versa
2. **Predictable Patterns**: Users learn once, apply everywhere
3. **Flexible Structure**: Adapt to content needs, not force fit
4. **Performance Focused**: Minimal DOM, efficient CSS
5. **Progressive Enhancement**: Mobile-first, enhance for larger screens

## Spatial Foundation

### The 8-Point Grid
All spacing derived from base unit of 8px:

```css
:root {
  /* Base unit */
  --unit: 8px;
  
  /* Spacing scale */
  --space-0: 0;                    /* 0px */
  --space-1: calc(var(--unit) * 1);   /* 8px */
  --space-2: calc(var(--unit) * 2);   /* 16px */
  --space-3: calc(var(--unit) * 3);   /* 24px */
  --space-4: calc(var(--unit) * 4);   /* 32px */
  --space-5: calc(var(--unit) * 5);   /* 40px */
  --space-6: calc(var(--unit) * 6);   /* 48px */
  --space-7: calc(var(--unit) * 7);   /* 56px */
  --space-8: calc(var(--unit) * 8);   /* 64px */
  --space-9: calc(var(--unit) * 9);   /* 72px */
  --space-10: calc(var(--unit) * 10); /* 80px */
  --space-12: calc(var(--unit) * 12); /* 96px */
  --space-16: calc(var(--unit) * 16); /* 128px */
  --space-20: calc(var(--unit) * 20); /* 160px */
  --space-24: calc(var(--unit) * 24); /* 192px */
  --space-32: calc(var(--unit) * 32); /* 256px */
}
```

### Spacing Application
```css
/* Component spacing */
.component-spacing {
  /* Internal padding */
  padding: var(--space-3);         /* Default: 24px */
  
  /* Element gaps */
  gap: var(--space-2);             /* Default: 16px */
  
  /* External margins */
  margin-bottom: var(--space-4);   /* Default: 32px */
}

/* Section spacing */
.section-spacing {
  padding-top: var(--space-10);    /* 80px */
  padding-bottom: var(--space-10); /* 80px */
}

/* Micro spacing */
.micro-spacing {
  gap: var(--space-1);             /* 8px for tight groups */
}
```

## Layout Containers

### Container System
```css
:root {
  /* Container widths */
  --container-xs: 480px;   /* Mobile reading width */
  --container-sm: 640px;   /* Small tablet width */
  --container-md: 768px;   /* Default content width */
  --container-lg: 1024px;  /* Wide content width */
  --container-xl: 1280px;  /* Full feature width */
  --container-2xl: 1536px; /* Maximum site width */
  
  /* Content widths */
  --content-prose: 65ch;   /* Optimal reading width */
  --content-narrow: 45ch;  /* Constrained content */
  --content-wide: 90ch;    /* Extended content */
}

/* Base container */
.container {
  width: 100%;
  margin-left: auto;
  margin-right: auto;
  padding-left: var(--space-4);
  padding-right: var(--space-4);
}

/* Container variants */
.container-xs { max-width: var(--container-xs); }
.container-sm { max-width: var(--container-sm); }
.container-md { max-width: var(--container-md); }
.container-lg { max-width: var(--container-lg); }
.container-xl { max-width: var(--container-xl); }
.container-2xl { max-width: var(--container-2xl); }

/* Content containers */
.container-prose { max-width: var(--content-prose); }
.container-narrow { max-width: var(--content-narrow); }
.container-wide { max-width: var(--content-wide); }

/* Responsive padding */
@media (min-width: 768px) {
  .container {
    padding-left: var(--space-6);
    padding-right: var(--space-6);
  }
}

@media (min-width: 1024px) {
  .container {
    padding-left: var(--space-8);
    padding-right: var(--space-8);
  }
}
```

## Grid Systems

### CSS Grid Foundation
```css
/* Base grid */
.grid {
  display: grid;
  gap: var(--space-4); /* 32px default gap */
}

/* Column-based grids */
.grid-1 { grid-template-columns: 1fr; }
.grid-2 { grid-template-columns: repeat(2, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-4 { grid-template-columns: repeat(4, 1fr); }
.grid-5 { grid-template-columns: repeat(5, 1fr); }
.grid-6 { grid-template-columns: repeat(6, 1fr); }

/* Auto-fit grids */
.grid-auto {
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}

.grid-auto-sm {
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}

.grid-auto-lg {
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

/* Responsive grids */
@media (max-width: 768px) {
  .grid-2,
  .grid-3,
  .grid-4,
  .grid-5,
  .grid-6 {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 768px) and (max-width: 1024px) {
  .grid-3,
  .grid-4,
  .grid-5,
  .grid-6 {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

### Advanced Grid Patterns
```css
/* Asymmetric grids */
.grid-sidebar {
  grid-template-columns: 300px 1fr;
  gap: var(--space-6);
}

.grid-sidebar-right {
  grid-template-columns: 1fr 300px;
  gap: var(--space-6);
}

.grid-featured {
  grid-template-columns: 2fr 1fr;
  gap: var(--space-4);
}

/* Holy grail layout */
.grid-holy-grail {
  display: grid;
  grid-template-areas:
    "header header header"
    "nav content aside"
    "footer footer footer";
  grid-template-rows: auto 1fr auto;
  grid-template-columns: 200px 1fr 200px;
  min-height: 100vh;
}

/* Card grid with auto-flow */
.grid-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-4);
  align-items: start;
}

/* Masonry-style (CSS Grid Level 3) */
.grid-masonry {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  grid-auto-rows: 10px;
  gap: var(--space-3);
}

.grid-masonry-item {
  grid-row-end: span var(--span, 20);
}
```

## Flexbox Layouts

### Flex Utilities
```css
/* Base flex container */
.flex {
  display: flex;
}

/* Direction */
.flex-row { flex-direction: row; }
.flex-col { flex-direction: column; }
.flex-row-reverse { flex-direction: row-reverse; }
.flex-col-reverse { flex-direction: column-reverse; }

/* Wrap */
.flex-wrap { flex-wrap: wrap; }
.flex-nowrap { flex-wrap: nowrap; }
.flex-wrap-reverse { flex-wrap: wrap-reverse; }

/* Justify content */
.justify-start { justify-content: flex-start; }
.justify-end { justify-content: flex-end; }
.justify-center { justify-content: center; }
.justify-between { justify-content: space-between; }
.justify-around { justify-content: space-around; }
.justify-evenly { justify-content: space-evenly; }

/* Align items */
.items-start { align-items: flex-start; }
.items-end { align-items: flex-end; }
.items-center { align-items: center; }
.items-baseline { align-items: baseline; }
.items-stretch { align-items: stretch; }

/* Align content */
.content-start { align-content: flex-start; }
.content-end { align-content: flex-end; }
.content-center { align-content: center; }
.content-between { align-content: space-between; }
.content-around { align-content: space-around; }
.content-stretch { align-content: stretch; }

/* Flex properties */
.flex-1 { flex: 1 1 0%; }
.flex-auto { flex: 1 1 auto; }
.flex-initial { flex: 0 1 auto; }
.flex-none { flex: none; }

/* Gap */
.gap-0 { gap: 0; }
.gap-1 { gap: var(--space-1); }
.gap-2 { gap: var(--space-2); }
.gap-3 { gap: var(--space-3); }
.gap-4 { gap: var(--space-4); }
.gap-5 { gap: var(--space-5); }
.gap-6 { gap: var(--space-6); }
.gap-8 { gap: var(--space-8); }
```

### Common Flex Patterns
```css
/* Navigation bar */
.nav-flex {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
}

/* Card layout */
.card-flex {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

/* Button group */
.button-group {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

/* Media object */
.media-flex {
  display: flex;
  gap: var(--space-3);
  align-items: flex-start;
}

/* Centered content */
.center-flex {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}
```

## Page Layouts

### Application Shell
```css
/* Full height app */
.app-shell {
  display: grid;
  grid-template-rows: auto 1fr auto;
  grid-template-columns: auto 1fr;
  grid-template-areas:
    "header header"
    "sidebar main"
    "sidebar footer";
  min-height: 100vh;
}

.app-header {
  grid-area: header;
  height: var(--header-height, 64px);
  border-bottom: 1px solid var(--border-default);
}

.app-sidebar {
  grid-area: sidebar;
  width: var(--sidebar-width, 250px);
  border-right: 1px solid var(--border-default);
  overflow-y: auto;
}

.app-main {
  grid-area: main;
  overflow-y: auto;
  padding: var(--space-6);
}

.app-footer {
  grid-area: footer;
  border-top: 1px solid var(--border-default);
  padding: var(--space-4);
}

/* Collapsible sidebar */
.app-shell.sidebar-collapsed {
  grid-template-columns: 0 1fr;
}

.app-shell.sidebar-collapsed .app-sidebar {
  width: 0;
  overflow: hidden;
}

/* Mobile adaptation */
@media (max-width: 768px) {
  .app-shell {
    grid-template-areas:
      "header"
      "main"
      "footer";
    grid-template-columns: 1fr;
  }
  
  .app-sidebar {
    position: fixed;
    left: -100%;
    top: var(--header-height, 64px);
    height: calc(100vh - var(--header-height, 64px));
    z-index: 100;
    transition: left 0.3s ease;
  }
  
  .app-sidebar.open {
    left: 0;
  }
}
```

### Content Layouts
```css
/* Article layout */
.article-layout {
  display: grid;
  grid-template-columns: 1fr min(65ch, 100%) 1fr;
  gap: var(--space-4);
}

.article-layout > * {
  grid-column: 2;
}

.article-layout .full-bleed {
  grid-column: 1 / -1;
}

/* Documentation layout */
.docs-layout {
  display: grid;
  grid-template-columns: 250px 1fr 250px;
  gap: var(--space-6);
  max-width: var(--container-xl);
  margin: 0 auto;
}

.docs-nav { position: sticky; top: var(--space-4); }
.docs-content { min-width: 0; }
.docs-toc { position: sticky; top: var(--space-4); }

/* Dashboard layout */
.dashboard-layout {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: var(--space-4);
}

.dashboard-widget-sm { grid-column: span 3; }
.dashboard-widget-md { grid-column: span 6; }
.dashboard-widget-lg { grid-column: span 9; }
.dashboard-widget-full { grid-column: span 12; }
```

## Responsive Breakpoints

### Breakpoint System
```css
:root {
  /* Breakpoints */
  --breakpoint-xs: 480px;
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1536px;
}

/* Mobile first approach */
/* Default: 0-479px */

/* Extra small devices */
@media (min-width: 480px) {
  .xs\:grid-2 { grid-template-columns: repeat(2, 1fr); }
  .xs\:flex-row { flex-direction: row; }
}

/* Small devices */
@media (min-width: 640px) {
  .sm\:grid-2 { grid-template-columns: repeat(2, 1fr); }
  .sm\:grid-3 { grid-template-columns: repeat(3, 1fr); }
  .sm\:flex-row { flex-direction: row; }
}

/* Medium devices */
@media (min-width: 768px) {
  .md\:grid-2 { grid-template-columns: repeat(2, 1fr); }
  .md\:grid-3 { grid-template-columns: repeat(3, 1fr); }
  .md\:grid-4 { grid-template-columns: repeat(4, 1fr); }
  .md\:flex-row { flex-direction: row; }
  .md\:block { display: block; }
  .md\:hidden { display: none; }
}

/* Large devices */
@media (min-width: 1024px) {
  .lg\:grid-3 { grid-template-columns: repeat(3, 1fr); }
  .lg\:grid-4 { grid-template-columns: repeat(4, 1fr); }
  .lg\:grid-5 { grid-template-columns: repeat(5, 1fr); }
  .lg\:flex-row { flex-direction: row; }
  .lg\:block { display: block; }
  .lg\:hidden { display: none; }
}

/* Extra large devices */
@media (min-width: 1280px) {
  .xl\:grid-4 { grid-template-columns: repeat(4, 1fr); }
  .xl\:grid-5 { grid-template-columns: repeat(5, 1fr); }
  .xl\:grid-6 { grid-template-columns: repeat(6, 1fr); }
  .xl\:block { display: block; }
  .xl\:hidden { display: none; }
}
```

### Container Queries (Future)
```css
/* Progressive enhancement with container queries */
@supports (container-type: inline-size) {
  .responsive-card {
    container-type: inline-size;
  }
  
  @container (min-width: 400px) {
    .card-content {
      display: grid;
      grid-template-columns: 150px 1fr;
      gap: var(--space-3);
    }
  }
  
  @container (min-width: 600px) {
    .card-content {
      grid-template-columns: 200px 1fr;
      gap: var(--space-4);
    }
  }
}
```

## Layout Utilities

### Positioning
```css
/* Position types */
.static { position: static; }
.relative { position: relative; }
.absolute { position: absolute; }
.fixed { position: fixed; }
.sticky { position: sticky; }

/* Position values */
.inset-0 { top: 0; right: 0; bottom: 0; left: 0; }
.inset-x-0 { left: 0; right: 0; }
.inset-y-0 { top: 0; bottom: 0; }

.top-0 { top: 0; }
.right-0 { right: 0; }
.bottom-0 { bottom: 0; }
.left-0 { left: 0; }

/* Z-index scale */
.z-0 { z-index: 0; }
.z-10 { z-index: 10; }
.z-20 { z-index: 20; }
.z-30 { z-index: 30; }
.z-40 { z-index: 40; }
.z-50 { z-index: 50; }
.z-auto { z-index: auto; }
```

### Overflow
```css
.overflow-auto { overflow: auto; }
.overflow-hidden { overflow: hidden; }
.overflow-visible { overflow: visible; }
.overflow-scroll { overflow: scroll; }

.overflow-x-auto { overflow-x: auto; }
.overflow-y-auto { overflow-y: auto; }
.overflow-x-hidden { overflow-x: hidden; }
.overflow-y-hidden { overflow-y: hidden; }
```

### Display
```css
.block { display: block; }
.inline { display: inline; }
.inline-block { display: inline-block; }
.flex { display: flex; }
.inline-flex { display: inline-flex; }
.grid { display: grid; }
.inline-grid { display: inline-grid; }
.hidden { display: none; }
```

## Layout Patterns

### Split Screen
```css
.split-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 100vh;
}

.split-fixed {
  display: grid;
  grid-template-columns: 500px 1fr;
  min-height: 100vh;
}

@media (max-width: 1024px) {
  .split-layout,
  .split-fixed {
    grid-template-columns: 1fr;
  }
}
```

### Sticky Elements
```css
/* Sticky header */
.sticky-header {
  position: sticky;
  top: 0;
  z-index: 40;
  background: var(--surface-primary);
  border-bottom: 1px solid var(--border-default);
}

/* Sticky sidebar */
.sticky-sidebar {
  position: sticky;
  top: calc(var(--header-height) + var(--space-4));
  max-height: calc(100vh - var(--header-height) - var(--space-8));
  overflow-y: auto;
}

/* Sticky footer */
.sticky-footer {
  position: sticky;
  bottom: 0;
  background: var(--surface-primary);
  border-top: 1px solid var(--border-default);
}
```

### Overlay Patterns
```css
/* Modal overlay */
.overlay {
  position: fixed;
  inset: 0;
  background: var(--surface-scrim);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

/* Drawer */
.drawer {
  position: fixed;
  top: 0;
  bottom: 0;
  width: 320px;
  background: var(--surface-primary);
  box-shadow: 0 0 20px rgba(0,0,0,0.1);
  z-index: 60;
  transform: translateX(-100%);
  transition: transform 0.3s ease;
}

.drawer.open {
  transform: translateX(0);
}

.drawer-right {
  right: 0;
  left: auto;
  transform: translateX(100%);
}
```

## Performance Considerations

### Layout Optimization
```css
/* Prevent layout shift */
.aspect-ratio-16-9 {
  position: relative;
  padding-bottom: 56.25%;
}

.aspect-ratio-16-9 > * {
  position: absolute;
  inset: 0;
}

/* Contain layout */
.contain-layout {
  contain: layout;
}

.contain-all {
  contain: layout style paint;
}

/* Hardware acceleration */
.will-transform {
  will-change: transform;
}
```

### Critical Layout CSS
```css
/* Inline critical layout CSS */
:root {
  --header-height: 64px;
  --sidebar-width: 250px;
}

.app-shell {
  display: grid;
  grid-template-rows: var(--header-height) 1fr;
  min-height: 100vh;
}
```

## Migration Strategy

### From Float-based Layouts
```css
/* Old */
.old-layout {
  float: left;
  width: 33.333%;
  padding: 10px;
}

/* New */
.new-layout {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
}
```

### From Fixed Widths
```css
/* Old */
.fixed-container {
  width: 960px;
  margin: 0 auto;
}

/* New */
.fluid-container {
  max-width: var(--container-lg);
  margin: 0 auto;
  padding: 0 var(--space-4);
}
```

## Testing Checklist

- [ ] Test all breakpoints
- [ ] Verify container widths
- [ ] Check grid alignment
- [ ] Validate spacing consistency
- [ ] Test sticky elements
- [ ] Verify overflow behavior
- [ ] Check z-index stacking
- [ ] Test print layouts