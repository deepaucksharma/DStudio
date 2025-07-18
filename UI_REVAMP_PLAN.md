# DStudio UI Revamp Plan

## Executive Summary
A comprehensive design system to transform DStudio into a beautiful, minimal, Google-inspired flat design while maintaining excellent usability and accessibility.

## Core Design Philosophy
**"Clarity through Simplicity"** - Every element serves a purpose, nothing is decorative.

### Design Principles
1. **Minimal Complexity**: Remove visual noise, focus on content
2. **Consistent Rhythm**: 8-point grid system throughout
3. **Purposeful Color**: Monochromatic base with strategic accent usage
4. **Clear Hierarchy**: Typography and spacing create natural flow
5. **Subtle Depth**: Light borders and shadows, no heavy elevation
6. **Performance First**: System fonts, efficient CSS, minimal dependencies

## 1. Foundation System

### Grid & Spacing
```css
:root {
  /* Base unit for consistent spacing */
  --base-unit: 8px;
  
  /* Spacing scale */
  --space-0: 0;
  --space-1: 8px;
  --space-2: 16px;
  --space-3: 24px;
  --space-4: 32px;
  --space-5: 40px;
  --space-6: 48px;
  --space-7: 56px;
  --space-8: 64px;
  --space-9: 72px;
  --space-10: 80px;
  --space-12: 96px;
  --space-16: 128px;
  --space-20: 160px;
  --space-24: 192px;
  
  /* Layout widths */
  --content-narrow: 600px;    /* Text-heavy content */
  --content-optimal: 680px;   /* Primary reading width */
  --content-wide: 960px;      /* Tools, calculators */
  --content-full: 1200px;     /* Complex layouts */
  --site-max: 1440px;         /* Maximum site width */
  
  /* Component dimensions */
  --header-height: 64px;
  --sidebar-width: 280px;
  --sidebar-collapsed: 64px;
}
```

### Typography System
```css
:root {
  /* Font families - Performance optimized */
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
               "Helvetica Neue", Arial, sans-serif;
  --font-mono: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", 
               Consolas, "Courier New", monospace;
  
  /* Type scale - Major Third (1.25) ratio */
  --text-xs: 0.75rem;     /* 12px - Captions, labels */
  --text-sm: 0.875rem;    /* 14px - Secondary text */
  --text-base: 1rem;      /* 16px - Body text */
  --text-lg: 1.25rem;     /* 20px - Emphasized body */
  --text-xl: 1.5rem;      /* 24px - Section headers */
  --text-2xl: 1.875rem;   /* 30px - Page headers */
  --text-3xl: 2.25rem;    /* 36px - Major headers */
  --text-4xl: 3rem;       /* 48px - Hero text */
  --text-5xl: 3.75rem;    /* 60px - Display text */
  
  /* Font weights */
  --font-light: 300;
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  
  /* Line heights */
  --leading-none: 1;
  --leading-tight: 1.25;
  --leading-snug: 1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  --leading-loose: 1.75;
  
  /* Letter spacing */
  --tracking-tighter: -0.05em;
  --tracking-tight: -0.025em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;
  --tracking-wider: 0.05em;
  --tracking-widest: 0.1em;
}
```

### Color System
```css
:root {
  /* Neutral palette - True grays */
  --gray-50: #FAFAFA;
  --gray-100: #F5F5F5;
  --gray-200: #EEEEEE;
  --gray-300: #E0E0E0;
  --gray-400: #BDBDBD;
  --gray-500: #9E9E9E;
  --gray-600: #757575;
  --gray-700: #616161;
  --gray-800: #424242;
  --gray-900: #212121;
  --gray-950: #121212;
  
  /* Primary - Refined Indigo */
  --primary-50: #E8EAF6;
  --primary-100: #C5CAE9;
  --primary-200: #9FA8DA;
  --primary-300: #7986CB;
  --primary-400: #5C6BC0;
  --primary-500: #3F51B5;
  --primary-600: #3949AB;
  --primary-700: #303F9F;
  --primary-800: #283593;
  --primary-900: #1A237E;
  
  /* Semantic colors */
  --success-light: #4CAF50;
  --success-dark: #388E3C;
  --warning-light: #FF9800;
  --warning-dark: #F57C00;
  --error-light: #F44336;
  --error-dark: #D32F2F;
  --info-light: #2196F3;
  --info-dark: #1976D2;
  
  /* Surface colors */
  --surface-primary: #FFFFFF;
  --surface-secondary: var(--gray-50);
  --surface-tertiary: var(--gray-100);
  --surface-elevated: #FFFFFF;
  --surface-overlay: rgba(0, 0, 0, 0.04);
  --surface-scrim: rgba(0, 0, 0, 0.32);
  
  /* Text colors */
  --text-primary: var(--gray-900);
  --text-secondary: var(--gray-700);
  --text-tertiary: var(--gray-600);
  --text-disabled: var(--gray-400);
  --text-inverse: #FFFFFF;
  
  /* Border colors */
  --border-light: var(--gray-200);
  --border-default: var(--gray-300);
  --border-dark: var(--gray-400);
}

/* Dark mode palette */
@media (prefers-color-scheme: dark) {
  :root {
    --surface-primary: var(--gray-900);
    --surface-secondary: var(--gray-800);
    --surface-tertiary: var(--gray-700);
    --surface-elevated: var(--gray-800);
    
    --text-primary: var(--gray-50);
    --text-secondary: var(--gray-300);
    --text-tertiary: var(--gray-400);
    
    --border-light: var(--gray-700);
    --border-default: var(--gray-600);
    --border-dark: var(--gray-500);
  }
}
```

## 2. Component Library

### Buttons
```css
/* Base button */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  line-height: var(--leading-tight);
  border-radius: 4px;
  transition: all 0.2s ease;
  cursor: pointer;
  border: none;
  text-decoration: none;
  white-space: nowrap;
  user-select: none;
}

/* Primary - Main actions only */
.btn-primary {
  background: var(--primary-600);
  color: var(--text-inverse);
}

.btn-primary:hover {
  background: var(--primary-700);
}

.btn-primary:active {
  background: var(--primary-800);
}

/* Secondary - Default choice */
.btn-secondary {
  background: var(--surface-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
}

.btn-secondary:hover {
  background: var(--surface-secondary);
  border-color: var(--border-dark);
}

/* Text - Minimal emphasis */
.btn-text {
  background: transparent;
  color: var(--primary-600);
  padding: var(--space-1) var(--space-2);
}

.btn-text:hover {
  background: var(--surface-overlay);
}

/* Sizes */
.btn-sm {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-sm);
}

.btn-lg {
  padding: var(--space-3) var(--space-6);
  font-size: var(--text-lg);
}

/* States */
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn:focus-visible {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}
```

### Cards
```css
.card {
  background: var(--surface-primary);
  border-radius: 8px;
  border: 1px solid var(--border-light);
  overflow: hidden;
  transition: all 0.2s ease;
}

.card-interactive {
  cursor: pointer;
}

.card-interactive:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: var(--border-default);
}

.card-header {
  padding: var(--space-4);
  border-bottom: 1px solid var(--border-light);
}

.card-body {
  padding: var(--space-4);
}

.card-footer {
  padding: var(--space-3) var(--space-4);
  background: var(--surface-secondary);
  border-top: 1px solid var(--border-light);
}

/* Card variations */
.card-elevated {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
  border: none;
}

.card-outlined {
  box-shadow: none;
  border: 1px solid var(--border-default);
}

.card-filled {
  background: var(--surface-secondary);
  border: none;
}
```

### Forms
```css
/* Input base */
.input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  color: var(--text-primary);
  background: var(--surface-primary);
  border: 1px solid var(--border-default);
  border-radius: 4px;
  transition: all 0.2s ease;
}

.input:hover {
  border-color: var(--border-dark);
}

.input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(63, 81, 181, 0.1);
}

.input:disabled {
  background: var(--surface-secondary);
  color: var(--text-disabled);
  cursor: not-allowed;
}

/* Input variations */
.input-error {
  border-color: var(--error-light);
}

.input-error:focus {
  box-shadow: 0 0 0 3px rgba(244, 67, 54, 0.1);
}

/* Labels */
.label {
  display: block;
  margin-bottom: var(--space-1);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
}

/* Help text */
.help-text {
  margin-top: var(--space-1);
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

/* Form groups */
.form-group {
  margin-bottom: var(--space-4);
}

/* Checkboxes and radios */
.checkbox,
.radio {
  display: flex;
  align-items: center;
  margin-bottom: var(--space-2);
  cursor: pointer;
}

.checkbox input,
.radio input {
  margin-right: var(--space-2);
}
```

### Navigation
```css
/* Top navigation bar */
.navbar {
  height: var(--header-height);
  background: var(--surface-primary);
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  padding: 0 var(--space-4);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-brand {
  font-size: var(--text-xl);
  font-weight: var(--font-normal);
  color: var(--text-primary);
  text-decoration: none;
  display: flex;
  align-items: center;
}

.navbar-nav {
  display: flex;
  align-items: center;
  margin-left: auto;
  gap: var(--space-1);
}

.navbar-link {
  padding: var(--space-2) var(--space-3);
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.navbar-link:hover {
  color: var(--text-primary);
  background: var(--surface-overlay);
}

.navbar-link.active {
  color: var(--primary-600);
  background: var(--primary-50);
}

/* Sidebar navigation */
.sidebar {
  width: var(--sidebar-width);
  background: var(--surface-secondary);
  border-right: 1px solid var(--border-light);
  height: 100%;
  overflow-y: auto;
}

.sidebar-section {
  padding: var(--space-2);
}

.sidebar-title {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  color: var(--text-tertiary);
  padding: var(--space-2) var(--space-3);
  margin-bottom: var(--space-1);
}

.sidebar-link {
  display: block;
  padding: var(--space-2) var(--space-3);
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.2s ease;
  margin-bottom: var(--space-1);
}

.sidebar-link:hover {
  color: var(--text-primary);
  background: var(--surface-overlay);
}

.sidebar-link.active {
  color: var(--primary-600);
  background: var(--primary-50);
  font-weight: var(--font-medium);
}

/* Tab navigation */
.tabs {
  display: flex;
  border-bottom: 1px solid var(--border-light);
  overflow-x: auto;
  scrollbar-width: none;
}

.tabs::-webkit-scrollbar {
  display: none;
}

.tab {
  padding: var(--space-3) var(--space-4);
  color: var(--text-secondary);
  text-decoration: none;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.tab:hover {
  color: var(--text-primary);
  background: var(--surface-overlay);
}

.tab.active {
  color: var(--primary-600);
  border-bottom-color: var(--primary-600);
}
```

### Tables
```css
.table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-base);
}

.table th {
  text-align: left;
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  padding: var(--space-3);
  border-bottom: 2px solid var(--border-light);
}

.table td {
  padding: var(--space-3);
  border-bottom: 1px solid var(--border-light);
  color: var(--text-primary);
}

.table tbody tr:hover {
  background: var(--surface-overlay);
}

/* Table variations */
.table-striped tbody tr:nth-child(even) {
  background: var(--surface-secondary);
}

.table-bordered {
  border: 1px solid var(--border-light);
}

.table-bordered th,
.table-bordered td {
  border: 1px solid var(--border-light);
}

.table-compact th,
.table-compact td {
  padding: var(--space-2);
}
```

### Alerts & Notifications
```css
.alert {
  padding: var(--space-3) var(--space-4);
  border-radius: 4px;
  border-left: 4px solid;
  margin-bottom: var(--space-4);
}

.alert-info {
  background: var(--info-light) + '10';
  border-left-color: var(--info-light);
  color: var(--info-dark);
}

.alert-success {
  background: var(--success-light) + '10';
  border-left-color: var(--success-light);
  color: var(--success-dark);
}

.alert-warning {
  background: var(--warning-light) + '10';
  border-left-color: var(--warning-light);
  color: var(--warning-dark);
}

.alert-error {
  background: var(--error-light) + '10';
  border-left-color: var(--error-light);
  color: var(--error-dark);
}

/* Toast notifications */
.toast {
  position: fixed;
  bottom: var(--space-4);
  right: var(--space-4);
  background: var(--gray-900);
  color: var(--text-inverse);
  padding: var(--space-3) var(--space-4);
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
```

## 3. Layout Patterns

### Page Structure
```css
/* Base layout */
.layout {
  display: flex;
  min-height: 100vh;
  background: var(--surface-primary);
}

.layout-sidebar {
  width: var(--sidebar-width);
  flex-shrink: 0;
}

.layout-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.layout-header {
  height: var(--header-height);
  flex-shrink: 0;
}

.layout-content {
  flex: 1;
  overflow-y: auto;
}

/* Content containers */
.container {
  width: 100%;
  margin: 0 auto;
  padding: 0 var(--space-4);
}

.container-narrow {
  max-width: var(--content-narrow);
}

.container-optimal {
  max-width: var(--content-optimal);
}

.container-wide {
  max-width: var(--content-wide);
}

.container-full {
  max-width: var(--content-full);
}

/* Section spacing */
.section {
  padding: var(--space-10) 0;
}

.section-compact {
  padding: var(--space-6) 0;
}

.section-spacious {
  padding: var(--space-16) 0;
}

/* Grid layouts */
.grid {
  display: grid;
  gap: var(--space-4);
}

.grid-2 {
  grid-template-columns: repeat(2, 1fr);
}

.grid-3 {
  grid-template-columns: repeat(3, 1fr);
}

.grid-4 {
  grid-template-columns: repeat(4, 1fr);
}

/* Responsive grids */
@media (max-width: 768px) {
  .grid-2,
  .grid-3,
  .grid-4 {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 768px) and (max-width: 1024px) {
  .grid-3,
  .grid-4 {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

### Content Typography
```css
/* Article content */
.article {
  font-size: var(--text-base);
  line-height: var(--leading-relaxed);
  color: var(--text-primary);
}

.article h1 {
  font-size: var(--text-3xl);
  font-weight: var(--font-light);
  line-height: var(--leading-tight);
  margin-bottom: var(--space-4);
  color: var(--text-primary);
}

.article h2 {
  font-size: var(--text-2xl);
  font-weight: var(--font-normal);
  line-height: var(--leading-tight);
  margin-top: var(--space-10);
  margin-bottom: var(--space-3);
  color: var(--text-primary);
}

.article h3 {
  font-size: var(--text-xl);
  font-weight: var(--font-medium);
  line-height: var(--leading-snug);
  margin-top: var(--space-8);
  margin-bottom: var(--space-2);
  color: var(--text-primary);
}

.article p {
  margin-bottom: var(--space-4);
}

.article ul,
.article ol {
  margin-bottom: var(--space-4);
  padding-left: var(--space-4);
}

.article li {
  margin-bottom: var(--space-2);
}

.article a {
  color: var(--primary-600);
  text-decoration: none;
  transition: color 0.2s ease;
}

.article a:hover {
  color: var(--primary-700);
  text-decoration: underline;
}

.article blockquote {
  border-left: 4px solid var(--border-default);
  padding-left: var(--space-4);
  margin: var(--space-6) 0;
  font-style: italic;
  color: var(--text-secondary);
}

.article code {
  font-family: var(--font-mono);
  font-size: 0.875em;
  padding: 2px 6px;
  background: var(--surface-secondary);
  border-radius: 3px;
  color: var(--primary-700);
}

.article pre {
  background: var(--surface-secondary);
  border: 1px solid var(--border-light);
  border-radius: 6px;
  padding: var(--space-4);
  overflow-x: auto;
  margin-bottom: var(--space-4);
}

.article pre code {
  background: none;
  padding: 0;
  color: inherit;
}
```

## 4. Interactive Elements

### Focus States
```css
/* Consistent focus indication */
:focus-visible {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}

/* Remove default focus for mouse users */
:focus:not(:focus-visible) {
  outline: none;
}
```

### Loading States
```css
/* Skeleton screens */
.skeleton {
  background: linear-gradient(
    90deg,
    var(--gray-200) 25%,
    var(--gray-100) 50%,
    var(--gray-200) 75%
  );
  background-size: 200% 100%;
  animation: loading 1.5s ease-in-out infinite;
  border-radius: 4px;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.skeleton-text {
  height: var(--text-base);
  margin-bottom: var(--space-2);
}

.skeleton-title {
  height: var(--text-2xl);
  margin-bottom: var(--space-4);
  width: 60%;
}

.skeleton-box {
  height: 100px;
  margin-bottom: var(--space-4);
}

/* Spinners */
.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid var(--gray-200);
  border-top-color: var(--primary-600);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Progress bars */
.progress {
  height: 4px;
  background: var(--gray-200);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: var(--primary-600);
  transition: width 0.3s ease;
}
```

### Transitions
```css
/* Standard transitions */
.transition-all {
  transition: all 0.2s ease;
}

.transition-colors {
  transition: color 0.2s ease, background-color 0.2s ease, 
              border-color 0.2s ease;
}

.transition-transform {
  transition: transform 0.2s ease;
}

.transition-opacity {
  transition: opacity 0.2s ease;
}

/* Hover effects */
.hover-grow:hover {
  transform: scale(1.05);
}

.hover-lift:hover {
  transform: translateY(-2px);
}

.hover-brightness:hover {
  filter: brightness(1.1);
}
```

## 5. Responsive Design

### Breakpoints
```css
/* Mobile first approach */
:root {
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1536px;
}

/* Media queries */
@media (min-width: 640px) {
  /* Small devices and up */
}

@media (min-width: 768px) {
  /* Medium devices and up */
}

@media (min-width: 1024px) {
  /* Large devices and up */
}

@media (min-width: 1280px) {
  /* Extra large devices and up */
}
```

### Mobile Adaptations
```css
/* Touch targets */
@media (hover: none) {
  .btn,
  .input,
  .checkbox,
  .radio {
    min-height: 44px;
  }
}

/* Mobile navigation */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: -100%;
    top: 0;
    height: 100%;
    z-index: 200;
    transition: left 0.3s ease;
  }
  
  .sidebar.open {
    left: 0;
  }
  
  .sidebar-overlay {
    position: fixed;
    inset: 0;
    background: var(--surface-scrim);
    z-index: 199;
    display: none;
  }
  
  .sidebar-overlay.show {
    display: block;
  }
}
```

## 6. Accessibility

### ARIA Labels
```css
/* Screen reader only text */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Focus within for better keyboard navigation */
.focus-within:focus-within {
  box-shadow: 0 0 0 3px rgba(63, 81, 181, 0.1);
}
```

### Color Contrast
- All text meets WCAG AA standards
- Primary text: 12.63:1 contrast ratio
- Secondary text: 7.43:1 contrast ratio
- Interactive elements: 4.5:1 minimum

## 7. Performance Optimizations

### CSS Architecture
```css
/* Critical CSS - Inline in <head> */
:root { /* Variables */ }
.layout { /* Base layout */ }
.navbar { /* Navigation */ }

/* Non-critical CSS - Load async */
.article { /* Content styles */ }
.card { /* Component styles */ }
```

### Animation Performance
```css
/* Use transform and opacity for animations */
.animate-slide {
  transform: translateX(0);
  transition: transform 0.3s ease;
}

/* Force GPU acceleration */
.gpu-accelerated {
  will-change: transform;
  transform: translateZ(0);
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## 8. Implementation Timeline

### Phase 1: Foundation (Week 1-2)
- [ ] Implement CSS variables
- [ ] Set up grid system
- [ ] Normalize typography
- [ ] Create color system
- [ ] Build base reset/normalize

### Phase 2: Core Components (Week 3-4)
- [ ] Design button system
- [ ] Create card components
- [ ] Build form elements
- [ ] Implement navigation patterns
- [ ] Design table styles

### Phase 3: Layout System (Week 5-6)
- [ ] Create page layouts
- [ ] Build responsive grid
- [ ] Implement sidebars
- [ ] Design content containers
- [ ] Add section spacing

### Phase 4: Interactive Elements (Week 7-8)
- [ ] Add loading states
- [ ] Create transitions
- [ ] Build modals/dialogs
- [ ] Implement tooltips
- [ ] Add micro-interactions

### Phase 5: Polish & Optimization (Week 9-10)
- [ ] Audit accessibility
- [ ] Optimize performance
- [ ] Add dark mode
- [ ] Create documentation
- [ ] Build component library

## 9. Migration Guide

### Step 1: Audit Current Styles
```bash
# Find all custom CSS files
find . -name "*.css" -o -name "*.scss"

# Identify inline styles
grep -r "style=" --include="*.html" --include="*.jsx"
```

### Step 2: Create Mapping
Map existing classes to new design system:
- `.btn-primary` → `.btn.btn-primary`
- `.card-wrapper` → `.card`
- `.content-area` → `.container.container-optimal`

### Step 3: Progressive Enhancement
1. Add new CSS alongside existing
2. Update components one section at a time
3. Remove old styles after verification
4. Test across browsers and devices

## 10. Component Examples

### Hero Section
```html
<section class="section section-spacious">
  <div class="container container-optimal">
    <h1 class="text-4xl font-light text-center mb-6">
      The Compendium of Distributed Systems
    </h1>
    <p class="text-xl text-secondary text-center mb-8">
      Master distributed systems through interactive learning
    </p>
    <div class="flex justify-center gap-4">
      <button class="btn btn-primary btn-lg">
        Get Started
      </button>
      <button class="btn btn-secondary btn-lg">
        View Examples
      </button>
    </div>
  </div>
</section>
```

### Feature Card Grid
```html
<div class="grid grid-3 gap-6">
  <div class="card card-interactive">
    <div class="card-body">
      <div class="icon-wrapper mb-4">
        <svg><!-- Icon --></svg>
      </div>
      <h3 class="text-xl font-medium mb-2">
        Interactive Tools
      </h3>
      <p class="text-secondary">
        Learn by doing with our suite of calculators and visualizers
      </p>
    </div>
  </div>
  <!-- More cards -->
</div>
```

### Navigation Implementation
```html
<nav class="navbar">
  <a href="/" class="navbar-brand">
    <img src="/logo.svg" alt="Logo" class="w-8 h-8 mr-3">
    DStudio
  </a>
  <div class="navbar-nav">
    <a href="/docs" class="navbar-link">Documentation</a>
    <a href="/tools" class="navbar-link active">Tools</a>
    <a href="/examples" class="navbar-link">Examples</a>
    <button class="btn btn-primary btn-sm ml-4">
      Sign In
    </button>
  </div>
</nav>
```

## 11. Design Tokens

### Export for Different Platforms
```javascript
// design-tokens.js
export const tokens = {
  color: {
    primary: {
      50: '#E8EAF6',
      100: '#C5CAE9',
      // ...
    },
    gray: {
      50: '#FAFAFA',
      100: '#F5F5F5',
      // ...
    }
  },
  spacing: {
    0: '0',
    1: '8px',
    2: '16px',
    // ...
  },
  typography: {
    fontFamily: {
      sans: '-apple-system, BlinkMacSystemFont...',
      mono: '"SF Mono", Monaco...'
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      // ...
    }
  }
};
```

### Sass Variables
```scss
// _variables.scss
$primary-50: #E8EAF6;
$primary-100: #C5CAE9;
// ...

$space-1: 8px;
$space-2: 16px;
// ...
```

### CSS-in-JS
```javascript
// theme.js
export const theme = {
  colors: {
    primary: '#3F51B5',
    gray50: '#FAFAFA',
    // ...
  },
  space: [0, 8, 16, 24, 32, 40, 48, 56, 64],
  // ...
};
```

## 12. Quality Checklist

### Visual Consistency
- [ ] All similar elements use same styles
- [ ] Consistent spacing throughout
- [ ] Color usage follows guidelines
- [ ] Typography hierarchy is clear
- [ ] Icons are from same family

### Performance
- [ ] CSS file < 50KB gzipped
- [ ] No unused styles
- [ ] Critical CSS inlined
- [ ] Images optimized
- [ ] Animations use transform/opacity

### Accessibility
- [ ] Color contrast passes WCAG AA
- [ ] Focus states visible
- [ ] Touch targets >= 44px
- [ ] Semantic HTML used
- [ ] ARIA labels where needed

### Responsiveness
- [ ] Mobile layout works
- [ ] Tablet layout works
- [ ] Desktop layout works
- [ ] No horizontal scroll
- [ ] Images scale properly

### Browser Support
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest 2 versions)
- [ ] Mobile browsers
- [ ] Progressive enhancement

## Conclusion

This comprehensive UI revamp plan transforms DStudio into a modern, minimal, and beautiful learning platform. The design system prioritizes:

1. **Clarity**: Every element has purpose
2. **Consistency**: Unified experience across all pages
3. **Performance**: Fast loading and smooth interactions
4. **Accessibility**: Usable by everyone
5. **Maintainability**: Easy to extend and modify

By following this plan, DStudio will achieve a Google-level flat design aesthetic while maintaining its unique identity as an interactive learning platform for distributed systems.