# Dark Mode Implementation

## Dark Mode Philosophy

### Core Principles
1. **True Dark Design**: Not just inverted colors, but thoughtfully adapted
2. **Reduced Eye Strain**: Optimized for low-light environments
3. **Consistent Experience**: Same usability in both modes
4. **Seamless Switching**: Instant, persistent preference
5. **Semantic Theming**: Colors adapt based on meaning, not just inversion

## Color Adaptation Strategy

### Background Hierarchy
```css
:root[data-theme="dark"] {
  /* Background layers - darker to lighter */
  --bg-base: #0A0A0A;        /* Deepest background */
  --bg-surface: #141414;     /* Card/component background */
  --bg-elevated: #1F1F1F;    /* Raised surfaces */
  --bg-overlay: #2A2A2A;     /* Modals, dropdowns */
  --bg-hover: rgba(255, 255, 255, 0.08);
  --bg-active: rgba(255, 255, 255, 0.12);
  --bg-selected: rgba(99, 102, 241, 0.2);
}

/* Light mode comparison */
:root[data-theme="light"] {
  --bg-base: #FAFAFA;
  --bg-surface: #FFFFFF;
  --bg-elevated: #FFFFFF;
  --bg-overlay: #FFFFFF;
  --bg-hover: rgba(0, 0, 0, 0.04);
  --bg-active: rgba(0, 0, 0, 0.08);
  --bg-selected: rgba(99, 102, 241, 0.1);
}
```

### Text Color Adaptation
```css
:root[data-theme="dark"] {
  /* Text hierarchy - lighter to darker */
  --text-primary: #F3F4F6;    /* 90% opacity white */
  --text-secondary: #D1D5DB;  /* 70% opacity white */
  --text-tertiary: #9CA3AF;   /* 50% opacity white */
  --text-disabled: #6B7280;   /* 30% opacity white */
  --text-inverse: #0A0A0A;    /* For light backgrounds */
}

:root[data-theme="light"] {
  --text-primary: #111827;
  --text-secondary: #4B5563;
  --text-tertiary: #6B7280;
  --text-disabled: #9CA3AF;
  --text-inverse: #FFFFFF;
}
```

### Border Adaptation
```css
:root[data-theme="dark"] {
  /* Borders - subtle in dark mode */
  --border-light: rgba(255, 255, 255, 0.08);
  --border-default: rgba(255, 255, 255, 0.12);
  --border-strong: rgba(255, 255, 255, 0.16);
  --border-focus: var(--primary-400);
}

:root[data-theme="light"] {
  --border-light: #F3F4F6;
  --border-default: #E5E7EB;
  --border-strong: #D1D5DB;
  --border-focus: var(--primary-600);
}
```

### Brand Colors in Dark Mode
```css
:root[data-theme="dark"] {
  /* Adjusted for dark backgrounds */
  --primary-50: rgba(99, 102, 241, 0.1);
  --primary-100: rgba(99, 102, 241, 0.2);
  --primary-200: rgba(99, 102, 241, 0.3);
  --primary-300: #6366F1;
  --primary-400: #818CF8;
  --primary-500: #A5B4FC;
  --primary-600: #C7D2FE;
  --primary-700: #DDD6FE;
  --primary-800: #E9D5FF;
  --primary-900: #F5F3FF;
  
  /* Primary for interactive elements */
  --primary-interactive: #818CF8;
  --primary-hover: #A5B4FC;
  --primary-active: #6366F1;
}
```

### Semantic Colors Adjustment
```css
:root[data-theme="dark"] {
  /* Success - less saturated */
  --success-bg: rgba(34, 197, 94, 0.1);
  --success-border: rgba(34, 197, 94, 0.3);
  --success-text: #86EFAC;
  --success-interactive: #4ADE80;
  
  /* Warning - warmer tone */
  --warning-bg: rgba(251, 146, 60, 0.1);
  --warning-border: rgba(251, 146, 60, 0.3);
  --warning-text: #FDBA74;
  --warning-interactive: #FB923C;
  
  /* Error - less harsh */
  --error-bg: rgba(239, 68, 68, 0.1);
  --error-border: rgba(239, 68, 68, 0.3);
  --error-text: #FCA5A5;
  --error-interactive: #F87171;
  
  /* Info - cooler tone */
  --info-bg: rgba(59, 130, 246, 0.1);
  --info-border: rgba(59, 130, 246, 0.3);
  --info-text: #93C5FD;
  --info-interactive: #60A5FA;
}
```

## Component Adaptations

### Cards & Surfaces
```css
/* Light mode card */
.card {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Dark mode card adjustments */
[data-theme="dark"] .card {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

/* Elevated surfaces */
[data-theme="dark"] .elevated {
  background: var(--bg-elevated);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4);
}

/* Nested surfaces */
[data-theme="dark"] .nested-surface {
  background: var(--bg-base);
  border-color: var(--border-light);
}
```

### Form Elements
```css
/* Input fields */
[data-theme="dark"] .input {
  background: var(--bg-base);
  border-color: var(--border-default);
  color: var(--text-primary);
  caret-color: var(--primary-interactive);
}

[data-theme="dark"] .input:hover {
  border-color: var(--border-strong);
  background: var(--bg-surface);
}

[data-theme="dark"] .input:focus {
  border-color: var(--primary-interactive);
  box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.2);
}

/* Select dropdowns */
[data-theme="dark"] .select {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%23D1D5DB' viewBox='0 0 20 20'%3E%3Cpath d='M7 7l3 3 3-3'/%3E%3C/svg%3E");
}

/* Checkboxes & Radios */
[data-theme="dark"] .checkbox,
[data-theme="dark"] .radio {
  background: var(--bg-base);
  border-color: var(--border-strong);
}

[data-theme="dark"] .checkbox:checked,
[data-theme="dark"] .radio:checked {
  background: var(--primary-interactive);
  border-color: var(--primary-interactive);
}
```

### Buttons
```css
/* Primary button */
[data-theme="dark"] .btn-primary {
  background: var(--primary-interactive);
  color: var(--bg-base);
}

[data-theme="dark"] .btn-primary:hover {
  background: var(--primary-hover);
}

/* Secondary button */
[data-theme="dark"] .btn-secondary {
  background: transparent;
  color: var(--text-primary);
  border-color: var(--border-strong);
}

[data-theme="dark"] .btn-secondary:hover {
  background: var(--bg-hover);
  border-color: var(--text-tertiary);
}

/* Ghost button */
[data-theme="dark"] .btn-ghost {
  color: var(--primary-interactive);
}

[data-theme="dark"] .btn-ghost:hover {
  background: rgba(129, 140, 248, 0.1);
}
```

### Navigation
```css
/* Navigation bar */
[data-theme="dark"] .navbar {
  background: var(--bg-surface);
  border-bottom-color: var(--border-light);
}

/* Nav links */
[data-theme="dark"] .nav-link {
  color: var(--text-secondary);
}

[data-theme="dark"] .nav-link:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

[data-theme="dark"] .nav-link.active {
  color: var(--primary-interactive);
  background: rgba(129, 140, 248, 0.1);
}

/* Sidebar */
[data-theme="dark"] .sidebar {
  background: var(--bg-surface);
  border-right-color: var(--border-light);
}
```

### Data Visualization
```css
/* Chart colors for dark mode */
[data-theme="dark"] {
  --chart-grid: rgba(255, 255, 255, 0.1);
  --chart-text: var(--text-secondary);
  --chart-1: #818CF8;  /* Primary */
  --chart-2: #F59E0B;  /* Amber */
  --chart-3: #10B981;  /* Emerald */
  --chart-4: #06B6D4;  /* Cyan */
  --chart-5: #8B5CF6;  /* Violet */
  --chart-6: #EF4444;  /* Red */
  --chart-7: #F97316;  /* Orange */
  --chart-8: #6B7280;  /* Gray */
}

/* Table stripes */
[data-theme="dark"] .table-striped tbody tr:nth-child(even) {
  background: var(--bg-hover);
}

[data-theme="dark"] .table tbody tr:hover {
  background: var(--bg-active);
}
```

## Shadow & Elevation

### Shadow Adaptation
```css
[data-theme="dark"] {
  /* Darker, more pronounced shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.4);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.5);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.6);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.7);
  --shadow-2xl: 0 25px 50px rgba(0, 0, 0, 0.8);
  
  /* Colored shadows */
  --shadow-primary: 0 4px 14px rgba(129, 140, 248, 0.3);
  --shadow-success: 0 4px 14px rgba(34, 197, 94, 0.3);
  --shadow-error: 0 4px 14px rgba(239, 68, 68, 0.3);
}

[data-theme="light"] {
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.1);
  --shadow-2xl: 0 25px 50px rgba(0, 0, 0, 0.25);
}
```

### Elevation System
```css
/* Dark mode elevation through background lightening */
[data-theme="dark"] {
  .elevation-0 { background: var(--bg-base); }
  .elevation-1 { background: var(--bg-surface); }
  .elevation-2 { background: var(--bg-elevated); }
  .elevation-3 { background: #252525; }
  .elevation-4 { background: #2A2A2A; }
}

/* Modal overlays */
[data-theme="dark"] .modal-backdrop {
  background: rgba(0, 0, 0, 0.8);
}

[data-theme="light"] .modal-backdrop {
  background: rgba(0, 0, 0, 0.5);
}
```

## Special Considerations

### Code Blocks
```css
/* Syntax highlighting for dark mode */
[data-theme="dark"] .code-block {
  background: #0D1117;
  border-color: var(--border-light);
}

[data-theme="dark"] .token.comment { color: #8B949E; }
[data-theme="dark"] .token.keyword { color: #FF7B72; }
[data-theme="dark"] .token.string { color: #A5D6FF; }
[data-theme="dark"] .token.function { color: #D2A8FF; }
[data-theme="dark"] .token.number { color: #79C0FF; }
[data-theme="dark"] .token.operator { color: #FF7B72; }
[data-theme="dark"] .token.class { color: #FFA657; }
```

### Images & Media
```css
/* Dim images in dark mode */
[data-theme="dark"] img:not(.no-dim) {
  opacity: 0.9;
  transition: opacity 0.2s ease;
}

[data-theme="dark"] img:not(.no-dim):hover {
  opacity: 1;
}

/* Invert diagrams */
[data-theme="dark"] .diagram-light {
  filter: invert(1) hue-rotate(180deg);
}

/* Dark mode specific images */
.image-adaptive {
  content: var(--image-light);
}

[data-theme="dark"] .image-adaptive {
  content: var(--image-dark);
}
```

### Scrollbars
```css
/* Custom scrollbar for dark mode */
[data-theme="dark"] {
  scrollbar-width: thin;
  scrollbar-color: var(--border-strong) var(--bg-base);
}

[data-theme="dark"]::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}

[data-theme="dark"]::-webkit-scrollbar-track {
  background: var(--bg-base);
}

[data-theme="dark"]::-webkit-scrollbar-thumb {
  background: var(--border-strong);
  border-radius: 6px;
  border: 3px solid var(--bg-base);
}

[data-theme="dark"]::-webkit-scrollbar-thumb:hover {
  background: var(--border-default);
}
```

## Implementation Strategy

### Theme Detection
```javascript
// System preference detection
const getSystemTheme = () => {
  return window.matchMedia('(prefers-color-scheme: dark)').matches 
    ? 'dark' 
    : 'light';
};

// Watch for system changes
window.matchMedia('(prefers-color-scheme: dark)')
  .addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) {
      setTheme(e.matches ? 'dark' : 'light');
    }
  });

// Theme persistence
const getStoredTheme = () => localStorage.getItem('theme');
const setStoredTheme = (theme) => localStorage.setItem('theme', theme);

// Apply theme
const setTheme = (theme) => {
  document.documentElement.setAttribute('data-theme', theme);
  setStoredTheme(theme);
};

// Initialize
const initTheme = () => {
  const stored = getStoredTheme();
  const theme = stored || getSystemTheme();
  setTheme(theme);
};
```

### Theme Toggle
```html
<!-- Theme toggle button -->
<button 
  class="theme-toggle" 
  aria-label="Toggle dark mode"
  data-theme-toggle
>
  <svg class="icon-light" viewBox="0 0 24 24">
    <!-- Sun icon -->
  </svg>
  <svg class="icon-dark" viewBox="0 0 24 24">
    <!-- Moon icon -->
  </svg>
</button>
```

```css
/* Toggle button styling */
.theme-toggle {
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg-hover);
  border: 1px solid var(--border-default);
  cursor: pointer;
  transition: all 0.2s ease;
}

.theme-toggle:hover {
  background: var(--bg-active);
}

.theme-toggle svg {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 20px;
  height: 20px;
  transition: opacity 0.2s ease, transform 0.2s ease;
}

[data-theme="light"] .icon-dark,
[data-theme="dark"] .icon-light {
  opacity: 0;
  transform: translate(-50%, -50%) rotate(180deg);
}

[data-theme="light"] .icon-light,
[data-theme="dark"] .icon-dark {
  opacity: 1;
  transform: translate(-50%, -50%) rotate(0);
}
```

### Transition Effects
```css
/* Smooth theme transitions */
:root {
  transition: background-color 0.3s ease, color 0.3s ease;
}

* {
  transition: background-color 0.3s ease, 
              border-color 0.3s ease,
              box-shadow 0.3s ease;
}

/* Prevent transition on page load */
.no-transitions * {
  transition: none !important;
}
```

```javascript
// Prevent flash of transitions on load
document.documentElement.classList.add('no-transitions');
window.addEventListener('load', () => {
  setTimeout(() => {
    document.documentElement.classList.remove('no-transitions');
  }, 100);
});
```

## Performance Optimization

### CSS Organization
```css
/* Base theme variables in separate file */
@import 'themes/light.css';
@import 'themes/dark.css' (prefers-color-scheme: dark);

/* Critical dark mode styles inline */
@media (prefers-color-scheme: dark) {
  :root {
    --bg-base: #0A0A0A;
    --text-primary: #F3F4F6;
  }
}
```

### Lazy Loading Theme Assets
```javascript
// Load theme-specific assets
const loadThemeAssets = async (theme) => {
  if (theme === 'dark') {
    // Load dark mode specific CSS
    await import('./styles/dark-mode-extras.css');
    
    // Swap images
    document.querySelectorAll('[data-theme-image]').forEach(img => {
      img.src = img.dataset.darkSrc || img.src;
    });
  }
};
```

## Testing & Validation

### Visual Testing Checklist
- [ ] All text meets contrast requirements
- [ ] Interactive elements are clearly visible
- [ ] Shadows provide appropriate depth
- [ ] Images/media are properly handled
- [ ] No pure white on pure black
- [ ] Focus states are visible
- [ ] Error states maintain meaning
- [ ] Charts/graphs remain readable

### Automated Testing
```javascript
// Contrast ratio testing
const getContrastRatio = (color1, color2) => {
  // Implementation of WCAG contrast calculation
};

// Test all color combinations
const testContrast = () => {
  const results = [];
  
  // Test text on backgrounds
  const textColors = ['--text-primary', '--text-secondary'];
  const bgColors = ['--bg-base', '--bg-surface', '--bg-elevated'];
  
  textColors.forEach(text => {
    bgColors.forEach(bg => {
      const ratio = getContrastRatio(
        getComputedStyle(root).getPropertyValue(text),
        getComputedStyle(root).getPropertyValue(bg)
      );
      
      results.push({
        text,
        background: bg,
        ratio,
        passes: ratio >= 4.5
      });
    });
  });
  
  return results;
};
```