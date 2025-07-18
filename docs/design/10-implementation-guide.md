# Implementation Guide

## Implementation Overview

This guide provides step-by-step instructions for implementing the DStudio design system in your project. Follow these guidelines to ensure consistent, maintainable, and performant implementation.

## Project Setup

### File Structure
```
/styles
├── /base
│   ├── reset.css          # CSS reset/normalize
│   ├── variables.css      # Design tokens
│   └── global.css         # Global styles
├── /components
│   ├── buttons.css        # Button components
│   ├── cards.css          # Card components
│   ├── forms.css          # Form components
│   └── navigation.css     # Navigation components
├── /layouts
│   ├── grid.css           # Grid system
│   ├── containers.css     # Container layouts
│   └── patterns.css       # Layout patterns
├── /themes
│   ├── light.css          # Light theme variables
│   └── dark.css           # Dark theme variables
├── /utilities
│   ├── spacing.css        # Spacing utilities
│   ├── typography.css     # Typography utilities
│   └── responsive.css     # Responsive utilities
└── main.css               # Main entry point
```

### CSS Architecture
```css
/* main.css - Import order matters */

/* 1. Base layer - Reset and variables */
@import 'base/reset.css';
@import 'base/variables.css';
@import 'base/global.css';

/* 2. Theme layer */
@import 'themes/light.css';
@import 'themes/dark.css' layer(theme);

/* 3. Layout layer */
@import 'layouts/grid.css' layer(layout);
@import 'layouts/containers.css' layer(layout);
@import 'layouts/patterns.css' layer(layout);

/* 4. Component layer */
@import 'components/buttons.css' layer(components);
@import 'components/cards.css' layer(components);
@import 'components/forms.css' layer(components);
@import 'components/navigation.css' layer(components);

/* 5. Utility layer - Highest specificity */
@import 'utilities/spacing.css' layer(utilities);
@import 'utilities/typography.css' layer(utilities);
@import 'utilities/responsive.css' layer(utilities);

/* Layer order definition */
@layer reset, theme, layout, components, utilities;
```

## Core Implementation

### 1. Design Tokens Setup
```css
/* base/variables.css */
:root {
  /* Color Tokens */
  --color-primary-50: #E8EAF6;
  --color-primary-100: #C5CAE9;
  --color-primary-200: #9FA8DA;
  --color-primary-300: #7986CB;
  --color-primary-400: #5C6BC0;
  --color-primary-500: #3F51B5;
  --color-primary-600: #3949AB;
  --color-primary-700: #303F9F;
  --color-primary-800: #283593;
  --color-primary-900: #1A237E;
  
  /* Spacing Tokens */
  --space-0: 0;
  --space-1: 0.25rem;  /* 4px */
  --space-2: 0.5rem;   /* 8px */
  --space-3: 0.75rem;  /* 12px */
  --space-4: 1rem;     /* 16px */
  --space-5: 1.25rem;  /* 20px */
  --space-6: 1.5rem;   /* 24px */
  --space-8: 2rem;     /* 32px */
  --space-10: 2.5rem;  /* 40px */
  --space-12: 3rem;    /* 48px */
  --space-16: 4rem;    /* 64px */
  
  /* Typography Tokens */
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
               Oxygen, Ubuntu, Cantarell, "Fira Sans", "Droid Sans", 
               "Helvetica Neue", Arial, sans-serif;
  --font-mono: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", 
               Consolas, "Courier New", monospace;
  
  /* Semantic Tokens */
  --bg-primary: var(--color-white);
  --bg-secondary: var(--color-gray-50);
  --text-primary: var(--color-gray-900);
  --text-secondary: var(--color-gray-700);
  --border-default: var(--color-gray-300);
}
```

### 2. Component Implementation
```css
/* components/buttons.css */

/* Base button styles */
.btn {
  /* Layout */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  
  /* Spacing */
  padding: var(--space-2) var(--space-4);
  
  /* Typography */
  font-family: var(--font-sans);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  line-height: var(--leading-tight);
  text-decoration: none;
  
  /* Visual */
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  
  /* Behavior */
  cursor: pointer;
  user-select: none;
  transition: all var(--duration-fast) var(--ease-out);
  
  /* States */
  &:hover {
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  &:focus-visible {
    outline: 2px solid var(--color-primary-500);
    outline-offset: 2px;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
}

/* Button variants */
.btn-primary {
  background: var(--color-primary-600);
  border-color: var(--color-primary-600);
  color: var(--color-white);
  
  &:hover {
    background: var(--color-primary-700);
    border-color: var(--color-primary-700);
  }
}

.btn-secondary {
  background: transparent;
  border-color: var(--border-default);
  color: var(--text-primary);
  
  &:hover {
    background: var(--bg-secondary);
    border-color: var(--border-strong);
  }
}

/* Size modifiers */
.btn-sm {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-sm);
}

.btn-lg {
  padding: var(--space-3) var(--space-6);
  font-size: var(--text-lg);
}
```

### 3. Layout Implementation
```css
/* layouts/grid.css */

/* Container */
.container {
  width: 100%;
  max-width: var(--container-max);
  margin-inline: auto;
  padding-inline: var(--container-padding);
}

/* Grid system */
.grid {
  display: grid;
  gap: var(--grid-gap, var(--space-4));
}

/* Auto-responsive grid */
.grid-auto {
  grid-template-columns: repeat(
    auto-fit, 
    minmax(var(--grid-min, 280px), 1fr)
  );
}

/* Fixed column grids */
.grid-2 { grid-template-columns: repeat(2, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-4 { grid-template-columns: repeat(4, 1fr); }

/* Responsive modifiers */
@container (min-width: 768px) {
  .md\:grid-2 { grid-template-columns: repeat(2, 1fr); }
  .md\:grid-3 { grid-template-columns: repeat(3, 1fr); }
  .md\:grid-4 { grid-template-columns: repeat(4, 1fr); }
}
```

## JavaScript Integration

### 1. Theme Management
```javascript
// theme-manager.js
class ThemeManager {
  constructor() {
    this.theme = this.getStoredTheme() || this.getSystemTheme();
    this.init();
  }
  
  init() {
    // Apply initial theme
    this.applyTheme(this.theme);
    
    // Watch for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)')
      .addEventListener('change', (e) => {
        if (!this.hasStoredTheme()) {
          this.applyTheme(e.matches ? 'dark' : 'light');
        }
      });
  }
  
  applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    this.theme = theme;
  }
  
  toggle() {
    const newTheme = this.theme === 'light' ? 'dark' : 'light';
    this.applyTheme(newTheme);
    this.storeTheme(newTheme);
  }
  
  getSystemTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches 
      ? 'dark' 
      : 'light';
  }
  
  getStoredTheme() {
    return localStorage.getItem('theme');
  }
  
  storeTheme(theme) {
    localStorage.setItem('theme', theme);
  }
  
  hasStoredTheme() {
    return localStorage.getItem('theme') !== null;
  }
}

// Initialize
const themeManager = new ThemeManager();

// Export for use in components
export default themeManager;
```

### 2. Component JavaScript
```javascript
// components/dropdown.js
class Dropdown {
  constructor(element) {
    this.element = element;
    this.trigger = element.querySelector('[data-dropdown-trigger]');
    this.content = element.querySelector('[data-dropdown-content]');
    this.isOpen = false;
    
    this.init();
  }
  
  init() {
    // Bind events
    this.trigger.addEventListener('click', this.toggle.bind(this));
    document.addEventListener('click', this.handleOutsideClick.bind(this));
    document.addEventListener('keydown', this.handleKeyboard.bind(this));
    
    // Set initial ARIA attributes
    this.trigger.setAttribute('aria-expanded', 'false');
    this.content.setAttribute('aria-hidden', 'true');
  }
  
  toggle() {
    this.isOpen ? this.close() : this.open();
  }
  
  open() {
    this.isOpen = true;
    this.element.classList.add('is-open');
    this.trigger.setAttribute('aria-expanded', 'true');
    this.content.setAttribute('aria-hidden', 'false');
    
    // Focus first focusable element
    const firstFocusable = this.content.querySelector(
      'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (firstFocusable) {
      firstFocusable.focus();
    }
  }
  
  close() {
    this.isOpen = false;
    this.element.classList.remove('is-open');
    this.trigger.setAttribute('aria-expanded', 'false');
    this.content.setAttribute('aria-hidden', 'true');
    this.trigger.focus();
  }
  
  handleOutsideClick(event) {
    if (this.isOpen && !this.element.contains(event.target)) {
      this.close();
    }
  }
  
  handleKeyboard(event) {
    if (!this.isOpen) return;
    
    if (event.key === 'Escape') {
      this.close();
    }
  }
}

// Initialize all dropdowns
document.querySelectorAll('[data-dropdown]').forEach(element => {
  new Dropdown(element);
});
```

## Build Process

### 1. PostCSS Configuration
```javascript
// postcss.config.js
module.exports = {
  plugins: [
    // Import handling
    require('postcss-import'),
    
    // Future CSS features
    require('postcss-preset-env')({
      stage: 3,
      features: {
        'nesting-rules': true,
        'custom-media-queries': true,
        'cascade-layers': true,
      }
    }),
    
    // Custom properties optimization
    require('postcss-custom-properties')({
      preserve: true,
      importFrom: './styles/base/variables.css'
    }),
    
    // Optimization
    require('cssnano')({
      preset: ['default', {
        discardComments: {
          removeAll: true,
        },
      }]
    }),
  ]
};
```

### 2. Build Scripts
```json
// package.json
{
  "scripts": {
    "build:css": "postcss styles/main.css -o dist/styles.css",
    "build:css:watch": "postcss styles/main.css -o dist/styles.css --watch",
    "build:js": "rollup -c rollup.config.js",
    "build:js:watch": "rollup -c rollup.config.js --watch",
    "build": "npm run build:css && npm run build:js",
    "dev": "concurrently \"npm:build:css:watch\" \"npm:build:js:watch\"",
    "optimize:css": "purgecss --css dist/styles.css --content dist/**/*.html --output dist/styles.min.css",
    "optimize:images": "imagemin src/images/* --out-dir=dist/images",
    "lint:css": "stylelint \"styles/**/*.css\"",
    "lint:js": "eslint \"src/**/*.js\"",
    "format": "prettier --write \"**/*.{css,js,html,json}\""
  }
}
```

### 3. Component Documentation
```markdown
# Button Component

## Usage

```html
<!-- Primary button -->
<button class="btn btn-primary">
  Click me
</button>

<!-- Secondary button -->
<button class="btn btn-secondary">
  Cancel
</button>

<!-- With icon -->
<button class="btn btn-primary">
  <svg class="icon" aria-hidden="true">...</svg>
  Save changes
</button>

<!-- Loading state -->
<button class="btn btn-primary" data-loading="true">
  Loading...
</button>
```

## Props

| Class | Description |
|-------|-------------|
| `.btn` | Base button styles |
| `.btn-primary` | Primary action button |
| `.btn-secondary` | Secondary action button |
| `.btn-ghost` | Text-only button |
| `.btn-sm` | Small size |
| `.btn-lg` | Large size |

## States

- `:hover` - Elevated appearance
- `:active` - Pressed appearance
- `:focus-visible` - Visible focus ring
- `:disabled` - Reduced opacity, no interactions
- `[data-loading]` - Shows loading spinner
```

## Testing Strategy

### 1. Visual Regression Testing
```javascript
// visual-tests/button.test.js
import { test } from '@playwright/test';

test.describe('Button Component', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/components/button');
  });
  
  test('default state', async ({ page }) => {
    await expect(page.locator('.btn-primary')).toHaveScreenshot();
  });
  
  test('hover state', async ({ page }) => {
    await page.hover('.btn-primary');
    await expect(page.locator('.btn-primary')).toHaveScreenshot();
  });
  
  test('focus state', async ({ page }) => {
    await page.focus('.btn-primary');
    await expect(page.locator('.btn-primary')).toHaveScreenshot();
  });
  
  test('dark mode', async ({ page }) => {
    await page.evaluate(() => {
      document.documentElement.setAttribute('data-theme', 'dark');
    });
    await expect(page.locator('.btn-primary')).toHaveScreenshot();
  });
});
```

### 2. Unit Testing
```javascript
// tests/theme-manager.test.js
import { describe, it, expect, beforeEach } from 'vitest';
import ThemeManager from '../src/theme-manager';

describe('ThemeManager', () => {
  let themeManager;
  
  beforeEach(() => {
    localStorage.clear();
    themeManager = new ThemeManager();
  });
  
  it('should detect system theme', () => {
    const mockMatchMedia = (matches) => ({
      matches,
      addEventListener: () => {},
    });
    
    window.matchMedia = mockMatchMedia(true);
    expect(themeManager.getSystemTheme()).toBe('dark');
    
    window.matchMedia = mockMatchMedia(false);
    expect(themeManager.getSystemTheme()).toBe('light');
  });
  
  it('should toggle theme', () => {
    themeManager.applyTheme('light');
    themeManager.toggle();
    expect(themeManager.theme).toBe('dark');
    
    themeManager.toggle();
    expect(themeManager.theme).toBe('light');
  });
  
  it('should persist theme preference', () => {
    themeManager.storeTheme('dark');
    expect(localStorage.getItem('theme')).toBe('dark');
  });
});
```

## Performance Optimization

### 1. Critical CSS
```html
<!-- Inline critical CSS -->
<style>
  /* Critical styles for above-the-fold content */
  :root {
    --color-primary-600: #3949AB;
    --space-4: 1rem;
    --font-sans: -apple-system, BlinkMacSystemFont, sans-serif;
  }
  
  body {
    margin: 0;
    font-family: var(--font-sans);
    line-height: 1.5;
  }
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--space-4);
  }
  
  /* ... other critical styles ... */
</style>

<!-- Load full CSS asynchronously -->
<link rel="preload" href="/styles.css" as="style">
<link rel="stylesheet" href="/styles.css" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="/styles.css"></noscript>
```

### 2. Component Lazy Loading
```javascript
// Lazy load heavy components
const loadHeavyComponent = async () => {
  const { HeavyComponent } = await import('./components/heavy-component.js');
  return new HeavyComponent();
};

// Intersection Observer for lazy loading
const lazyComponents = document.querySelectorAll('[data-lazy-component]');

const componentObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const componentName = entry.target.dataset.lazyComponent;
      import(`./components/${componentName}.js`).then(module => {
        new module.default(entry.target);
      });
      componentObserver.unobserve(entry.target);
    }
  });
});

lazyComponents.forEach(el => componentObserver.observe(el));
```

## Migration Checklist

- [ ] Set up file structure
- [ ] Import design tokens
- [ ] Implement base styles
- [ ] Create component styles
- [ ] Set up build process
- [ ] Implement theme switching
- [ ] Add responsive utilities
- [ ] Create documentation
- [ ] Set up testing
- [ ] Optimize performance
- [ ] Train team
- [ ] Monitor adoption