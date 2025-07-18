# Responsive Design Specifications

## Responsive Philosophy

### Core Principles
1. **Mobile-First**: Build for small screens, enhance for larger
2. **Content Priority**: Most important content always visible
3. **Fluid Everything**: Flexible grids, images, and typography
4. **Touch-Friendly**: Minimum 44px touch targets on mobile
5. **Performance Matters**: Optimize assets for each breakpoint

## Breakpoint System

### Standard Breakpoints
```css
:root {
  /* Breakpoint values */
  --breakpoint-xs: 480px;   /* Small phones */
  --breakpoint-sm: 640px;   /* Large phones */
  --breakpoint-md: 768px;   /* Tablets */
  --breakpoint-lg: 1024px;  /* Small laptops */
  --breakpoint-xl: 1280px;  /* Desktops */
  --breakpoint-2xl: 1536px; /* Large screens */
  --breakpoint-3xl: 1920px; /* Ultra-wide */
}

/* Media query mixins */
@custom-media --xs-up (min-width: 480px);
@custom-media --sm-up (min-width: 640px);
@custom-media --md-up (min-width: 768px);
@custom-media --lg-up (min-width: 1024px);
@custom-media --xl-up (min-width: 1280px);
@custom-media --2xl-up (min-width: 1536px);

/* Max-width queries for targeting specific ranges */
@custom-media --xs-only (max-width: 639px);
@custom-media --sm-only (min-width: 640px) and (max-width: 767px);
@custom-media --md-only (min-width: 768px) and (max-width: 1023px);
@custom-media --lg-only (min-width: 1024px) and (max-width: 1279px);
```

### Device-Specific Considerations
```css
/* iPhone SE / Small phones */
@media (max-width: 375px) {
  :root {
    --container-padding: var(--space-3);
    --font-scale: 0.95;
  }
}

/* iPad / Tablets in portrait */
@media (min-width: 768px) and (max-width: 1023px) and (orientation: portrait) {
  :root {
    --columns: 8;
    --sidebar-width: 240px;
  }
}

/* iPad Pro / Large tablets */
@media (min-width: 1024px) and (max-width: 1366px) {
  :root {
    --columns: 12;
    --max-content-width: 960px;
  }
}

/* Desktop and beyond */
@media (min-width: 1920px) {
  :root {
    --max-content-width: 1400px;
    --font-scale: 1.1;
  }
}
```

## Responsive Typography

### Fluid Type Scale
```css
/* Fluid typography with clamp() */
:root {
  /* Body text */
  --text-base-fluid: clamp(
    0.875rem,  /* 14px minimum */
    1rem,      /* 16px preferred */
    1.125rem   /* 18px maximum */
  );
  
  /* Headings */
  --h1-fluid: clamp(1.75rem, 4vw + 1rem, 3.5rem);
  --h2-fluid: clamp(1.5rem, 3vw + 0.75rem, 2.5rem);
  --h3-fluid: clamp(1.25rem, 2vw + 0.5rem, 2rem);
  --h4-fluid: clamp(1.125rem, 1.5vw + 0.5rem, 1.5rem);
  --h5-fluid: clamp(1rem, 1vw + 0.5rem, 1.25rem);
  --h6-fluid: clamp(0.875rem, 0.5vw + 0.5rem, 1rem);
}

/* Responsive line height */
body {
  line-height: calc(1.5 + 0.2 * ((100vw - 320px) / 680));
}

/* Responsive letter spacing */
h1, h2, h3 {
  letter-spacing: calc(-0.02em + 0.01 * ((100vw - 320px) / 680));
}
```

### Breakpoint-Based Typography
```css
/* Mobile defaults */
body {
  font-size: 16px;
  line-height: 1.6;
}

h1 { font-size: 1.75rem; }
h2 { font-size: 1.5rem; }
h3 { font-size: 1.25rem; }

/* Tablet and up */
@media (min-width: 768px) {
  body {
    font-size: 17px;
    line-height: 1.65;
  }
  
  h1 { font-size: 2.25rem; }
  h2 { font-size: 1.875rem; }
  h3 { font-size: 1.5rem; }
}

/* Desktop and up */
@media (min-width: 1024px) {
  body {
    font-size: 18px;
    line-height: 1.7;
  }
  
  h1 { font-size: 3rem; }
  h2 { font-size: 2.25rem; }
  h3 { font-size: 1.75rem; }
}
```

## Responsive Layout Patterns

### Container System
```css
/* Responsive container */
.container {
  width: 100%;
  margin-left: auto;
  margin-right: auto;
  padding-left: var(--container-padding);
  padding-right: var(--container-padding);
}

/* Container padding by breakpoint */
:root {
  --container-padding: var(--space-4); /* 16px default */
}

@media (min-width: 768px) {
  :root {
    --container-padding: var(--space-6); /* 24px */
  }
}

@media (min-width: 1024px) {
  :root {
    --container-padding: var(--space-8); /* 32px */
  }
}

/* Max widths by breakpoint */
@media (min-width: 640px) {
  .container-sm { max-width: 640px; }
}

@media (min-width: 768px) {
  .container-md { max-width: 768px; }
}

@media (min-width: 1024px) {
  .container-lg { max-width: 1024px; }
}

@media (min-width: 1280px) {
  .container-xl { max-width: 1280px; }
}
```

### Grid Responsiveness
```css
/* Mobile-first grid */
.grid {
  display: grid;
  gap: var(--space-4);
  grid-template-columns: 1fr; /* Single column mobile */
}

/* Progressive enhancement */
@media (min-width: 640px) {
  .sm\:grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
  .sm\:grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
  .sm\:grid-cols-4 { grid-template-columns: repeat(4, 1fr); }
}

@media (min-width: 768px) {
  .md\:grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
  .md\:grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
  .md\:grid-cols-4 { grid-template-columns: repeat(4, 1fr); }
  .md\:grid-cols-6 { grid-template-columns: repeat(6, 1fr); }
}

@media (min-width: 1024px) {
  .lg\:grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
  .lg\:grid-cols-4 { grid-template-columns: repeat(4, 1fr); }
  .lg\:grid-cols-6 { grid-template-columns: repeat(6, 1fr); }
  .lg\:grid-cols-12 { grid-template-columns: repeat(12, 1fr); }
}

/* Auto-fit responsive grid */
.grid-responsive {
  display: grid;
  gap: var(--space-4);
  grid-template-columns: repeat(
    auto-fit, 
    minmax(min(100%, 280px), 1fr)
  );
}
```

### Flexbox Responsiveness
```css
/* Stack on mobile, row on desktop */
.flex-responsive {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

@media (min-width: 768px) {
  .md\:flex-row { flex-direction: row; }
  .md\:flex-wrap { flex-wrap: wrap; }
  .md\:justify-between { justify-content: space-between; }
  .md\:items-center { align-items: center; }
}

/* Responsive flex items */
.flex-item {
  flex: 1 1 100%; /* Full width mobile */
}

@media (min-width: 768px) {
  .md\:flex-1 { flex: 1 1 0%; }
  .md\:flex-auto { flex: 1 1 auto; }
  .md\:flex-none { flex: none; }
  .md\:w-1\/2 { flex: 0 0 50%; }
  .md\:w-1\/3 { flex: 0 0 33.333%; }
  .md\:w-1\/4 { flex: 0 0 25%; }
}
```

## Component Responsiveness

### Navigation Patterns
```css
/* Mobile navigation (hamburger menu) */
.nav-mobile {
  display: block;
  position: fixed;
  top: 0;
  left: -100%;
  width: 80%;
  max-width: 320px;
  height: 100vh;
  background: var(--bg-surface);
  transition: left 0.3s ease;
  z-index: 100;
}

.nav-mobile.open {
  left: 0;
}

/* Desktop navigation */
@media (min-width: 1024px) {
  .nav-mobile {
    display: none;
  }
  
  .nav-desktop {
    display: flex;
    gap: var(--space-4);
  }
}

/* Responsive nav toggle */
.nav-toggle {
  display: block;
  width: 44px;
  height: 44px;
  padding: var(--space-2);
  cursor: pointer;
}

@media (min-width: 1024px) {
  .nav-toggle {
    display: none;
  }
}
```

### Card Responsiveness
```css
/* Responsive card grid */
.card-grid {
  display: grid;
  gap: var(--space-4);
  grid-template-columns: 1fr;
}

@media (min-width: 640px) {
  .card-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .card-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Responsive card layout */
.card-responsive {
  display: flex;
  flex-direction: column;
}

.card-image {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
}

@media (min-width: 768px) {
  .card-responsive {
    flex-direction: row;
  }
  
  .card-image {
    width: 200px;
    aspect-ratio: 1;
  }
}
```

### Table Responsiveness
```css
/* Responsive table wrapper */
.table-responsive {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

/* Mobile table transformation */
@media (max-width: 767px) {
  .table-mobile {
    display: block;
  }
  
  .table-mobile thead {
    display: none;
  }
  
  .table-mobile tbody,
  .table-mobile tr,
  .table-mobile td {
    display: block;
  }
  
  .table-mobile tr {
    margin-bottom: var(--space-4);
    border: 1px solid var(--border-light);
    border-radius: 8px;
    padding: var(--space-3);
  }
  
  .table-mobile td {
    display: flex;
    justify-content: space-between;
    padding: var(--space-2) 0;
    border: none;
  }
  
  .table-mobile td::before {
    content: attr(data-label);
    font-weight: var(--font-semibold);
  }
}
```

### Form Responsiveness
```css
/* Responsive form layout */
.form-responsive {
  display: grid;
  gap: var(--space-4);
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .form-row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-4);
  }
  
  .form-full {
    grid-column: 1 / -1;
  }
}

/* Responsive input groups */
.input-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

@media (min-width: 640px) {
  .input-group-inline {
    flex-direction: row;
    align-items: center;
  }
  
  .input-group-inline .input {
    flex: 1;
  }
}

/* Touch-friendly inputs on mobile */
@media (max-width: 767px) {
  input,
  select,
  textarea,
  button {
    min-height: 44px;
    font-size: 16px; /* Prevents zoom on iOS */
  }
}
```

## Responsive Images & Media

### Image Responsiveness
```css
/* Responsive images */
img {
  max-width: 100%;
  height: auto;
  display: block;
}

/* Art direction with picture element */
picture img {
  width: 100%;
  height: auto;
  object-fit: cover;
}

/* Responsive background images */
.hero-image {
  background-image: url('hero-mobile.jpg');
  background-size: cover;
  background-position: center;
  height: 300px;
}

@media (min-width: 768px) {
  .hero-image {
    background-image: url('hero-tablet.jpg');
    height: 400px;
  }
}

@media (min-width: 1024px) {
  .hero-image {
    background-image: url('hero-desktop.jpg');
    height: 500px;
  }
}

/* Responsive aspect ratios */
.aspect-video {
  aspect-ratio: 16 / 9;
}

.aspect-square {
  aspect-ratio: 1 / 1;
}

@supports not (aspect-ratio: 1) {
  /* Fallback for older browsers */
  .aspect-video {
    position: relative;
    padding-bottom: 56.25%;
  }
  
  .aspect-video > * {
    position: absolute;
    inset: 0;
  }
}
```

### Video Responsiveness
```css
/* Responsive video container */
.video-responsive {
  position: relative;
  padding-bottom: 56.25%; /* 16:9 aspect ratio */
  height: 0;
  overflow: hidden;
}

.video-responsive iframe,
.video-responsive video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

/* Responsive video with max-width */
.video-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}
```

## Responsive Utilities

### Visibility Utilities
```css
/* Hide/show by breakpoint */
.hidden { display: none !important; }
.block { display: block !important; }

@media (min-width: 640px) {
  .sm\:hidden { display: none !important; }
  .sm\:block { display: block !important; }
}

@media (min-width: 768px) {
  .md\:hidden { display: none !important; }
  .md\:block { display: block !important; }
  .md\:flex { display: flex !important; }
  .md\:grid { display: grid !important; }
}

@media (min-width: 1024px) {
  .lg\:hidden { display: none !important; }
  .lg\:block { display: block !important; }
}

/* Only show at specific breakpoints */
.mobile-only {
  display: block;
}

@media (min-width: 768px) {
  .mobile-only {
    display: none;
  }
}

.desktop-only {
  display: none;
}

@media (min-width: 1024px) {
  .desktop-only {
    display: block;
  }
}
```

### Spacing Utilities
```css
/* Responsive spacing */
.p-4 { padding: var(--space-4); }
.m-4 { margin: var(--space-4); }

@media (min-width: 768px) {
  .md\:p-6 { padding: var(--space-6); }
  .md\:m-6 { margin: var(--space-6); }
  .md\:px-8 { padding-left: var(--space-8); padding-right: var(--space-8); }
  .md\:py-8 { padding-top: var(--space-8); padding-bottom: var(--space-8); }
}

@media (min-width: 1024px) {
  .lg\:p-8 { padding: var(--space-8); }
  .lg\:m-8 { margin: var(--space-8); }
}
```

### Text Alignment
```css
/* Responsive text alignment */
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

@media (min-width: 768px) {
  .md\:text-left { text-align: left; }
  .md\:text-center { text-align: center; }
  .md\:text-right { text-align: right; }
}
```

## Performance Optimization

### Responsive Loading
```html
<!-- Responsive images with srcset -->
<img 
  src="image-small.jpg"
  srcset="
    image-small.jpg 480w,
    image-medium.jpg 768w,
    image-large.jpg 1200w,
    image-xlarge.jpg 2000w
  "
  sizes="
    (max-width: 480px) 100vw,
    (max-width: 768px) 80vw,
    (max-width: 1200px) 60vw,
    50vw
  "
  alt="Responsive image"
>

<!-- Art direction with picture -->
<picture>
  <source 
    media="(min-width: 1024px)" 
    srcset="desktop.webp" 
    type="image/webp"
  >
  <source 
    media="(min-width: 768px)" 
    srcset="tablet.webp" 
    type="image/webp"
  >
  <source 
    srcset="mobile.webp" 
    type="image/webp"
  >
  <img src="fallback.jpg" alt="Responsive image">
</picture>
```

### CSS Loading Strategy
```html
<!-- Critical CSS inline -->
<style>
  /* Mobile-first critical styles */
  .container { padding: 16px; }
  .grid { display: grid; gap: 16px; }
</style>

<!-- Responsive CSS loading -->
<link rel="stylesheet" href="mobile.css">
<link 
  rel="stylesheet" 
  href="tablet.css" 
  media="(min-width: 768px)"
>
<link 
  rel="stylesheet" 
  href="desktop.css" 
  media="(min-width: 1024px)"
>
```

### JavaScript Breakpoint Detection
```javascript
// Responsive JavaScript utilities
const breakpoints = {
  xs: 480,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536
};

// Get current breakpoint
const getCurrentBreakpoint = () => {
  const width = window.innerWidth;
  
  for (const [name, value] of Object.entries(breakpoints).reverse()) {
    if (width >= value) return name;
  }
  return 'xs';
};

// Breakpoint change listener
const onBreakpointChange = (callback) => {
  let currentBreakpoint = getCurrentBreakpoint();
  
  window.addEventListener('resize', () => {
    const newBreakpoint = getCurrentBreakpoint();
    if (newBreakpoint !== currentBreakpoint) {
      currentBreakpoint = newBreakpoint;
      callback(newBreakpoint);
    }
  });
};

// Usage
onBreakpointChange((breakpoint) => {
  console.log(`Breakpoint changed to: ${breakpoint}`);
  
  // Load/unload features based on breakpoint
  if (breakpoint === 'lg' || breakpoint === 'xl') {
    // Load desktop features
  } else {
    // Load mobile features
  }
});
```

## Testing Guidelines

### Device Testing Matrix
```yaml
Mobile Devices:
  - iPhone SE (375x667)
  - iPhone 12/13 (390x844)
  - iPhone 14 Pro Max (430x932)
  - Samsung Galaxy S21 (384x854)
  - Pixel 5 (393x851)

Tablets:
  - iPad Mini (768x1024)
  - iPad Air (820x1180)
  - iPad Pro 11" (834x1194)
  - iPad Pro 12.9" (1024x1366)
  - Surface Pro 7 (912x1368)

Desktops:
  - Small laptop (1280x800)
  - Standard laptop (1440x900)
  - Desktop (1920x1080)
  - 4K Display (3840x2160)
  - Ultrawide (3440x1440)
```

### Testing Checklist
- [ ] Content readable at all breakpoints
- [ ] Touch targets minimum 44px on mobile
- [ ] No horizontal scroll on mobile
- [ ] Images load appropriate size
- [ ] Forms usable on all devices
- [ ] Navigation accessible at all sizes
- [ ] Performance acceptable on 3G
- [ ] Orientation changes handled
- [ ] Zoom functionality not broken
- [ ] Print styles included

## Lessons Learned from Implementation

### Mobile-First Approach Success

Our implementation validated the mobile-first philosophy:

```css
/* Base styles for mobile */
.hero {
  padding: 4rem 2rem;
  text-align: center;
}

/* Enhance for larger screens */
@media (min-width: 768px) {
  .hero {
    padding: 6rem 4rem;
  }
}
```

**Benefits:**
- Simpler base CSS
- Progressive enhancement natural
- Better performance on mobile
- Easier to maintain

### Fluid Typography Implementation

#### 1. Clamp() for Responsive Text
```css
/* Successful fluid typography */
.hero h1 {
  font-size: clamp(2.5rem, 2rem + 2.5vw, 3.5rem);
}

.hero p {
  font-size: clamp(1.125rem, 1rem + 0.5vw, 1.5rem);
}
```

**Why it works:**
- Smooth scaling between breakpoints
- No jarring jumps at breakpoints
- Respects user preferences
- Reduces media queries

#### 2. Minimum Font Sizes
```css
/* Maintaining readability */
.md-typeset p {
  font-size: clamp(1rem, 0.95rem + 0.25vw, 1.125rem);
  /*               ^^^^ Never smaller than 16px */
}
```

**Key insight**: Never go below 16px for body text to maintain readability and prevent zoom on iOS.

### Responsive Grid Patterns

#### 1. Auto-Fill Grid Success
```css
/* Axiom grid that works everywhere */
.axiom-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
}
```

**Benefits:**
- No media queries needed
- Automatically responsive
- No orphaned items
- Consistent spacing

#### 2. Mobile Stack Pattern
```css
/* Hero stats grid */
.hero .stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}

@media (max-width: 768px) {
  .hero .stats {
    grid-template-columns: 1fr;
    gap: var(--space-md);
  }
}
```

### Critical Mobile Optimizations

#### 1. Full-Width Mobile Components
```css
/* Edge-to-edge hero on mobile */
@media (max-width: 768px) {
  .hero {
    margin: var(--space-md) calc(-1 * var(--space-md)) var(--space-xl);
    border-radius: 0;
  }
}
```

**Purpose**: Creates immersive mobile experience by extending components edge-to-edge.

#### 2. Touch-Friendly Interactions
```css
/* Implemented touch targets */
.hero-actions .md-button {
  padding: 0.75rem 2rem;
  min-height: 44px;
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .hero-actions {
    flex-direction: column;
  }
  
  .hero-actions .md-button {
    width: 100%;
    justify-content: center;
  }
}
```

### Responsive Spacing Strategy

#### 1. Dynamic Padding
```css
/* Content padding that scales */
.md-content {
  padding: var(--space-xl) var(--space-lg);
}

@media (max-width: 768px) {
  .md-content {
    padding: var(--space-lg) var(--space-md);
  }
}
```

**Rationale**: Smaller screens need tighter padding to maximize content area.

#### 2. Responsive Margins
```css
/* Component margins adjust */
.axiom-box,
.decision-box {
  margin: var(--space-xl) 0;
  padding: var(--space-lg);
}

@media (max-width: 768px) {
  .axiom-box,
  .decision-box {
    margin: var(--space-lg) 0;
    padding: var(--space-md);
  }
}
```

### Table Responsiveness Solutions

#### 1. Horizontal Scroll Pattern
```css
/* Simple table solution */
@media (max-width: 768px) {
  .md-typeset table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }
}
```

**Why this works:**
- Preserves table structure
- Allows horizontal scrolling
- Clear visual affordance
- Better than reformatting

### Common Responsive Pitfalls Avoided

1. **Fixed Font Sizes**: Always use relative units or clamp()
2. **Breakpoint Proliferation**: Stick to major breakpoints
3. **Desktop-First Mindset**: Mobile-first prevents overrides
4. **Forgetting Landscape**: Test mobile landscape orientation
5. **Ignoring Touch**: Ensure 44px minimum touch targets

### Performance Optimizations

#### 1. Efficient Media Queries
```css
/* Group related styles */
@media (max-width: 768px) {
  /* All mobile styles together */
  .hero { /* ... */ }
  .axiom-grid { /* ... */ }
  .hero-actions { /* ... */ }
}
```

#### 2. CSS Custom Properties for Responsiveness
```css
/* Define responsive values once */
:root {
  --content-padding: var(--space-lg);
}

@media (max-width: 768px) {
  :root {
    --content-padding: var(--space-md);
  }
}

/* Use everywhere */
.content {
  padding: var(--content-padding);
}
```

### Testing Insights from Implementation

#### Key Breakpoints That Matter
1. **375px**: iPhone SE (smallest common device)
2. **768px**: Tablet portrait / Mobile landscape
3. **1024px**: Desktop threshold
4. **1200px**: Content max-width

#### Visual Testing Discoveries
- Font size issues most visible on real devices
- Spacing problems apparent in landscape mode
- Touch target size critical for usability
- Performance varies greatly by device

### Responsive Patterns That Work

#### 1. Hero Section Pattern
```css
/* Mobile base */
.hero {
  padding: 4rem 2rem;
  border-radius: 1rem;
  margin: 2rem 0;
}

/* Tablet enhancement */
@media (min-width: 768px) {
  .hero {
    padding: 6rem 4rem;
  }
}

/* Mobile full-width */
@media (max-width: 768px) {
  .hero {
    margin-left: -1rem;
    margin-right: -1rem;
    border-radius: 0;
  }
}
```

#### 2. Button Group Pattern
```css
/* Flexible button layout */
.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

/* Stack on mobile */
@media (max-width: 768px) {
  .hero-actions {
    flex-direction: column;
  }
  
  .hero-actions > * {
    width: 100%;
  }
}
```

### Future Responsive Considerations

1. **Container Queries**: Would solve component-level responsiveness
2. **Preference Queries**: Respect reduced motion, contrast preferences
3. **Logical Properties**: Better internationalization support
4. **Variable Fonts**: Responsive typography axis

### Key Takeaways

1. **Mobile-First is Non-Negotiable**: Start small, enhance up
2. **Fluid Everything**: Typography, spacing, layouts
3. **Test Real Devices**: Simulators miss critical issues
4. **Performance Matters More on Mobile**: Every kb counts
5. **Accessibility and Responsiveness Go Hand-in-Hand**: They're not separate concerns