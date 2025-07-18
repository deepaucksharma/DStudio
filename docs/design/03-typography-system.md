# Typography System

## Typography Philosophy

### Core Principles
1. **Readability First**: Optimize for long-form reading
2. **Clear Hierarchy**: Guide the eye through content
3. **Consistent Rhythm**: Predictable spacing and sizing
4. **Performance**: System fonts for instant rendering
5. **Brand Consistency**: Unified typographic voice

## Font Stack Strategy

### System Font Stack
```css
/* Optimized for each platform's native experience */
--font-sans: -apple-system,           /* macOS/iOS Safari */
             BlinkMacSystemFont,      /* macOS Chrome */
             "Segoe UI",              /* Windows */
             Roboto,                  /* Android/Chrome OS */
             Oxygen,                  /* KDE */
             Ubuntu,                  /* Ubuntu */
             Cantarell,               /* GNOME */
             "Fira Sans",             /* Firefox OS */
             "Droid Sans",            /* Older Android */
             "Helvetica Neue",        /* Older macOS */
             Arial,                   /* Fallback */
             sans-serif;              /* Generic fallback */

/* Monospace for code */
--font-mono: "SF Mono",               /* macOS */
             Monaco,                  /* Older macOS */
             "Cascadia Code",         /* Windows Terminal */
             "Roboto Mono",           /* Google */
             "Ubuntu Mono",           /* Ubuntu */
             "Fira Code",             /* Popular choice */
             Consolas,                /* Windows */
             "Courier New",           /* Universal */
             monospace;               /* Generic fallback */
```

### Font Loading Strategy
```css
/* Prevent FOIT (Flash of Invisible Text) */
body {
  font-family: var(--font-sans);
  font-display: swap; /* Show fallback immediately */
}

/* Optional: Variable font future-proofing */
@supports (font-variation-settings: normal) {
  body {
    font-family: "Inter var", var(--font-sans);
  }
}
```

## Type Scale

### Scale System (Major Third - 1.25x)
```css
/* Base: 16px browser default */
--text-xs:   0.75rem;    /* 12px - Legal, captions */
--text-sm:   0.875rem;   /* 14px - Secondary content */
--text-base: 1rem;       /* 16px - Body text */
--text-lg:   1.25rem;    /* 20px - Lead paragraphs */
--text-xl:   1.5rem;     /* 24px - Section headers */
--text-2xl:  1.875rem;   /* 30px - Page headers */
--text-3xl:  2.25rem;    /* 36px - Major headers */
--text-4xl:  3rem;       /* 48px - Hero text */
--text-5xl:  3.75rem;    /* 60px - Display text */
--text-6xl:  4.5rem;     /* 72px - Marketing only */
```

### Responsive Type Scale
```css
/* Fluid typography with CSS clamp() */
--text-responsive-sm:  clamp(0.875rem, 0.8rem + 0.25vw, 1rem);
--text-responsive-base: clamp(1rem, 0.95rem + 0.25vw, 1.125rem);
--text-responsive-lg:  clamp(1.25rem, 1.15rem + 0.5vw, 1.5rem);
--text-responsive-xl:  clamp(1.5rem, 1.35rem + 0.75vw, 2rem);
--text-responsive-2xl: clamp(1.875rem, 1.65rem + 1.125vw, 2.5rem);
--text-responsive-3xl: clamp(2.25rem, 1.85rem + 2vw, 3.5rem);
--text-responsive-4xl: clamp(3rem, 2.25rem + 3.75vw, 5rem);
```

## Font Weights

### Weight Scale
```css
--font-thin:       100;  /* Not recommended - poor readability */
--font-extralight: 200;  /* Not recommended - poor readability */
--font-light:      300;  /* Display text only */
--font-normal:     400;  /* Body text default */
--font-medium:     500;  /* Slight emphasis */
--font-semibold:   600;  /* Buttons, nav items */
--font-bold:       700;  /* Strong emphasis */
--font-extrabold:  800;  /* Display headers */
--font-black:      900;  /* Maximum emphasis */
```

### Weight Usage Guidelines
```css
/* Body text - always normal */
body { font-weight: var(--font-normal); }

/* Headings - progressive weight */
h1 { font-weight: var(--font-light); }    /* Large = lighter */
h2 { font-weight: var(--font-normal); }   
h3 { font-weight: var(--font-medium); }
h4 { font-weight: var(--font-semibold); }
h5 { font-weight: var(--font-semibold); }
h6 { font-weight: var(--font-bold); }     /* Small = heavier */

/* UI elements */
.btn { font-weight: var(--font-medium); }
.nav-link { font-weight: var(--font-normal); }
.nav-link.active { font-weight: var(--font-semibold); }
```

## Line Heights

### Height Scale
```css
--leading-none:    1;      /* Display text only */
--leading-tight:   1.25;   /* Headings */
--leading-snug:    1.375;  /* Subheadings */
--leading-normal:  1.5;    /* UI elements */
--leading-relaxed: 1.625;  /* Body text */
--leading-loose:   1.75;   /* Readable paragraphs */
--leading-double:  2;      /* Special cases only */
```

### Line Height Application
```css
/* Headings - tighter for impact */
h1, h2 { line-height: var(--leading-tight); }
h3, h4 { line-height: var(--leading-snug); }
h5, h6 { line-height: var(--leading-normal); }

/* Body text - optimized for reading */
p, li { line-height: var(--leading-relaxed); }

/* Dense content */
.table { line-height: var(--leading-normal); }
.code { line-height: var(--leading-normal); }
```

## Letter Spacing

### Tracking Scale
```css
--tracking-tighter: -0.05em;   /* Display text only */
--tracking-tight:   -0.025em;  /* Large headings */
--tracking-normal:  0;          /* Body text default */
--tracking-wide:    0.025em;   /* Subtle emphasis */
--tracking-wider:   0.05em;    /* Small caps, labels */
--tracking-widest:  0.1em;     /* All caps text */
```

### Letter Spacing Usage
```css
/* Headings - tighten as size increases */
.text-4xl { letter-spacing: var(--tracking-tight); }
.text-3xl { letter-spacing: var(--tracking-tight); }
.text-2xl { letter-spacing: -0.01em; }

/* Body - always normal */
p { letter-spacing: var(--tracking-normal); }

/* UI elements */
.btn { letter-spacing: 0.01em; }  /* Slight spacing */
.label { 
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
}
```

## Typography Compositions

### Document Headers
```css
.article-header {
  /* Title */
  h1 {
    font-size: var(--text-responsive-3xl);
    font-weight: var(--font-light);
    line-height: var(--leading-tight);
    letter-spacing: var(--tracking-tight);
    margin-bottom: var(--space-4);
  }
  
  /* Subtitle */
  .subtitle {
    font-size: var(--text-responsive-xl);
    font-weight: var(--font-normal);
    line-height: var(--leading-snug);
    color: var(--text-secondary);
    margin-bottom: var(--space-6);
  }
  
  /* Meta */
  .meta {
    font-size: var(--text-sm);
    font-weight: var(--font-normal);
    line-height: var(--leading-normal);
    color: var(--text-tertiary);
  }
}
```

### Body Content
```css
.article-content {
  /* Paragraphs */
  p {
    font-size: var(--text-base);
    line-height: var(--leading-relaxed);
    margin-bottom: var(--space-4);
    max-width: 65ch; /* Optimal reading width */
  }
  
  /* Lead paragraph */
  p.lead {
    font-size: var(--text-lg);
    line-height: var(--leading-loose);
    color: var(--text-secondary);
    margin-bottom: var(--space-6);
  }
  
  /* Lists */
  ul, ol {
    font-size: var(--text-base);
    line-height: var(--leading-relaxed);
    margin-bottom: var(--space-4);
    padding-left: var(--space-6);
  }
  
  li {
    margin-bottom: var(--space-2);
  }
  
  /* Blockquotes */
  blockquote {
    font-size: var(--text-lg);
    font-style: italic;
    line-height: var(--leading-relaxed);
    border-left: 4px solid var(--border-default);
    padding-left: var(--space-4);
    margin: var(--space-6) 0;
  }
}
```

### UI Typography
```css
/* Navigation */
.nav-link {
  font-size: var(--text-base);
  font-weight: var(--font-normal);
  letter-spacing: 0.01em;
}

/* Buttons */
.btn {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  line-height: var(--leading-tight);
  letter-spacing: 0.02em;
}

.btn-sm { font-size: var(--text-sm); }
.btn-lg { font-size: var(--text-lg); }

/* Form labels */
.label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  line-height: var(--leading-normal);
  letter-spacing: 0.01em;
}

/* Input text */
.input {
  font-size: var(--text-base);
  line-height: var(--leading-normal);
}

/* Help text */
.help-text {
  font-size: var(--text-sm);
  line-height: var(--leading-normal);
  color: var(--text-tertiary);
}
```

## Specialized Typography

### Code Typography
```css
/* Inline code */
code {
  font-family: var(--font-mono);
  font-size: 0.875em; /* Relative to parent */
  font-weight: var(--font-normal);
  letter-spacing: 0;
  background: var(--surface-secondary);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
}

/* Code blocks */
pre {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
  tab-size: 2;
}

/* Syntax highlighting */
.token.comment { font-style: italic; }
.token.keyword { font-weight: var(--font-semibold); }
```

### Data Typography
```css
/* Tables */
.table {
  font-size: var(--text-base);
  line-height: var(--leading-normal);
}

.table th {
  font-weight: var(--font-semibold);
  letter-spacing: 0.01em;
}

/* Numbers */
.number {
  font-variant-numeric: tabular-nums; /* Align numbers */
  letter-spacing: 0.01em;
}

/* Statistics */
.stat-value {
  font-size: var(--text-4xl);
  font-weight: var(--font-light);
  line-height: var(--leading-none);
}

.stat-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  letter-spacing: var(--tracking-wider);
  text-transform: uppercase;
}
```

## Responsive Typography

### Mobile Adjustments
```css
@media (max-width: 768px) {
  /* Reduce heading sizes */
  h1 { font-size: var(--text-2xl); }
  h2 { font-size: var(--text-xl); }
  h3 { font-size: var(--text-lg); }
  
  /* Maintain button consistency */
  .btn { 
    font-size: var(--text-base);
  }
  
  /* Optimize paragraph spacing */
  p { 
    font-size: var(--text-base);
    line-height: var(--leading-relaxed);
  }
}
```

### Print Styles
```css
@media print {
  body {
    font-size: 12pt;
    line-height: 1.5;
    font-family: Georgia, "Times New Roman", serif;
  }
  
  h1 { font-size: 24pt; }
  h2 { font-size: 18pt; }
  h3 { font-size: 14pt; }
  
  p { 
    text-align: justify;
    hyphenate: auto;
  }
}
```

## International Typography

### Multi-language Support
```css
/* CJK Languages */
:lang(zh),
:lang(ja),
:lang(ko) {
  font-family: system-ui, sans-serif;
  line-height: 1.7; /* More space for characters */
  letter-spacing: 0.02em;
}

/* Arabic/Hebrew */
:lang(ar),
:lang(he) {
  direction: rtl;
  text-align: right;
  font-family: system-ui, sans-serif;
}

/* Devanagari scripts */
:lang(hi),
:lang(mr),
:lang(ne) {
  line-height: 1.8;
  font-family: system-ui, sans-serif;
}
```

## Performance Optimization

### Critical Font Loading
```html
<!-- Preload critical fonts -->
<link rel="preload" 
      href="/fonts/inter-var.woff2" 
      as="font" 
      type="font/woff2" 
      crossorigin>

<!-- Font face declaration -->
<style>
@font-face {
  font-family: 'Inter var';
  src: url('/fonts/inter-var.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-display: swap;
}
</style>
```

### Text Rendering Optimization
```css
body {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
  font-feature-settings: "kern" 1; /* Enable kerning */
}

/* Disable for performance on large blocks */
.large-text-block {
  text-rendering: auto;
}
```

## Typography Testing

### Readability Tests
1. **Line Length**: 45-75 characters optimal
2. **Contrast**: Strong visual hierarchy
3. **Size**: 16px base for body text
4. **Leading**: 1.5x-1.75x for comfortable reading

### Cross-browser Testing
```css
/* Feature detection */
@supports (font-variant-numeric: tabular-nums) {
  .table { font-variant-numeric: tabular-nums; }
}

@supports not (font-variant-numeric: tabular-nums) {
  .table { font-feature-settings: "tnum" 1; }
}
```

## Migration Checklist

- [ ] Audit current font usage
- [ ] Map old sizes to new scale
- [ ] Update CSS variables
- [ ] Test readability metrics
- [ ] Visual design review
- [ ] Cross-browser testing
- [ ] Performance benchmarking
- [ ] Documentation update