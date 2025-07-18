# Interactive Patterns

## Interaction Philosophy

### Core Principles
1. **Predictable Behavior**: Users can anticipate outcomes
2. **Immediate Feedback**: Every action has a visible response
3. **Natural Gestures**: Leverage platform conventions
4. **Progressive Disclosure**: Reveal complexity gradually
5. **Forgiving Interface**: Easy to recover from mistakes

## Hover States

### Standard Hover Behavior
```css
/* Universal hover transition */
.interactive {
  transition: all 0.2s ease;
  cursor: pointer;
}

/* Elevation on hover */
.hover-lift {
  transform: translateY(0);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Scale on hover */
.hover-scale:hover {
  transform: scale(1.05);
}

/* Brightness on hover */
.hover-brightness:hover {
  filter: brightness(1.1);
}

/* Reveal on hover */
.hover-reveal .hidden-content {
  opacity: 0;
  transition: opacity 0.3s ease;
}

.hover-reveal:hover .hidden-content {
  opacity: 1;
}
```

### Card Hover Patterns
```css
/* Card with hidden actions */
.card-hover {
  position: relative;
  overflow: hidden;
}

.card-hover-actions {
  position: absolute;
  top: var(--space-2);
  right: var(--space-2);
  opacity: 0;
  transform: translateY(-8px);
  transition: all 0.2s ease;
}

.card-hover:hover .card-hover-actions {
  opacity: 1;
  transform: translateY(0);
}

/* Card with overlay */
.card-overlay {
  position: relative;
}

.card-overlay::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, transparent, rgba(0, 0, 0, 0.5));
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.card-overlay:hover::before {
  opacity: 1;
}

/* Card content slide */
.card-slide {
  position: relative;
  overflow: hidden;
}

.card-slide-content {
  transform: translateY(100%);
  transition: transform 0.3s ease;
}

.card-slide:hover .card-slide-content {
  transform: translateY(0);
}
```

## Click & Tap Interactions

### Button Press Effects
```css
/* Depth press */
.btn-depth {
  position: relative;
  transform: translateY(0);
  box-shadow: 0 4px 0 var(--primary-800);
}

.btn-depth:active {
  transform: translateY(2px);
  box-shadow: 0 2px 0 var(--primary-800);
}

/* Ripple effect */
.btn-ripple {
  position: relative;
  overflow: hidden;
}

.btn-ripple::after {
  content: "";
  position: absolute;
  width: 100%;
  height: 100%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0);
  background: rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  opacity: 0;
}

.btn-ripple:active::after {
  animation: ripple 0.6s ease-out;
}

@keyframes ripple {
  0% {
    transform: translate(-50%, -50%) scale(0);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) scale(4);
    opacity: 0;
  }
}

/* Pulse on click */
.btn-pulse:active {
  animation: pulse 0.3s ease;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(0.95); }
  100% { transform: scale(1); }
}
```

### Selection States
```css
/* Multi-select items */
.selectable {
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s ease;
}

.selectable:hover {
  background: var(--surface-overlay);
}

.selectable.selected {
  background: var(--primary-50);
  border-color: var(--primary-500);
}

.selectable.selected::before {
  content: "✓";
  position: absolute;
  top: var(--space-2);
  right: var(--space-2);
  width: 20px;
  height: 20px;
  background: var(--primary-600);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

/* Toggle selection */
.toggle-select {
  position: relative;
  cursor: pointer;
}

.toggle-select input {
  position: absolute;
  opacity: 0;
}

.toggle-select-indicator {
  display: block;
  padding: var(--space-3);
  border: 2px solid var(--border-default);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.toggle-select input:checked ~ .toggle-select-indicator {
  background: var(--primary-50);
  border-color: var(--primary-500);
}
```

## Drag & Drop

### Draggable Elements
```css
.draggable {
  cursor: grab;
  transition: all 0.2s ease;
}

.draggable:hover {
  background: var(--surface-overlay);
}

.draggable:active {
  cursor: grabbing;
}

.draggable.is-dragging {
  opacity: 0.5;
  transform: scale(1.05);
  cursor: grabbing;
  z-index: 100;
}

/* Drag ghost */
.drag-ghost {
  position: fixed;
  pointer-events: none;
  z-index: 1000;
  transform: rotate(3deg);
  opacity: 0.8;
}

/* Drop zones */
.drop-zone {
  border: 2px dashed var(--border-default);
  border-radius: 8px;
  padding: var(--space-6);
  text-align: center;
  transition: all 0.2s ease;
}

.drop-zone.active {
  border-color: var(--primary-500);
  background: var(--primary-50);
}

.drop-zone.hover {
  border-color: var(--primary-600);
  background: var(--primary-100);
  transform: scale(1.02);
}
```

### Sortable Lists
```css
.sortable-list {
  list-style: none;
  padding: 0;
}

.sortable-item {
  background: var(--surface-primary);
  border: 1px solid var(--border-light);
  padding: var(--space-3);
  margin-bottom: var(--space-2);
  cursor: move;
  transition: all 0.2s ease;
}

.sortable-item:hover {
  background: var(--surface-secondary);
}

.sortable-item.is-dragging {
  opacity: 0.4;
  transform: scale(0.95);
}

.sortable-item.is-over {
  border-style: dashed;
  border-color: var(--primary-500);
}

/* Drag handle */
.drag-handle {
  cursor: grab;
  color: var(--text-tertiary);
  padding: var(--space-1);
  margin: calc(var(--space-1) * -1);
}

.drag-handle:active {
  cursor: grabbing;
}
```

## Form Interactions

### Input Focus States
```css
/* Enhanced focus */
.input-enhanced {
  position: relative;
  transition: all 0.2s ease;
}

.input-enhanced:focus {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(var(--primary-500-rgb), 0.15);
}

/* Floating labels */
.floating-label {
  position: relative;
}

.floating-label-input {
  padding-top: var(--space-4);
}

.floating-label-text {
  position: absolute;
  top: var(--space-3);
  left: var(--space-3);
  color: var(--text-tertiary);
  transition: all 0.2s ease;
  pointer-events: none;
}

.floating-label-input:focus ~ .floating-label-text,
.floating-label-input:not(:placeholder-shown) ~ .floating-label-text {
  top: var(--space-1);
  font-size: var(--text-xs);
  color: var(--primary-600);
}

/* Input with icon */
.input-icon {
  position: relative;
}

.input-icon-element {
  position: absolute;
  top: 50%;
  left: var(--space-3);
  transform: translateY(-50%);
  color: var(--text-tertiary);
  transition: color 0.2s ease;
}

.input-icon input {
  padding-left: var(--space-10);
}

.input-icon input:focus ~ .input-icon-element {
  color: var(--primary-600);
}
```

### Form Validation
```css
/* Real-time validation */
.field-validating .input {
  background-image: url("data:image/svg+xml,%3Csvg...");
  background-repeat: no-repeat;
  background-position: right var(--space-2) center;
  background-size: 20px;
}

.field-valid .input {
  border-color: var(--success-500);
  background-image: url("data:image/svg+xml,%3Csvg...");
  background-repeat: no-repeat;
  background-position: right var(--space-2) center;
  background-size: 20px;
}

.field-invalid .input {
  border-color: var(--error-500);
  background-image: url("data:image/svg+xml,%3Csvg...");
  background-repeat: no-repeat;
  background-position: right var(--space-2) center;
  background-size: 20px;
}

/* Error messages */
.field-error {
  max-height: 0;
  overflow: hidden;
  transition: all 0.3s ease;
}

.field-invalid .field-error {
  max-height: 100px;
  margin-top: var(--space-1);
}

/* Success animation */
@keyframes checkmark {
  0% {
    stroke-dashoffset: 100;
  }
  100% {
    stroke-dashoffset: 0;
  }
}

.field-valid .checkmark {
  animation: checkmark 0.3s ease-in-out;
}
```

## Loading & Progress

### Loading Patterns
```css
/* Button loading state */
.btn[data-loading="true"] {
  color: transparent;
  pointer-events: none;
}

.btn[data-loading="true"]::after {
  content: "";
  position: absolute;
  width: 16px;
  height: 16px;
  top: 50%;
  left: 50%;
  margin-left: -8px;
  margin-top: -8px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

/* Progress steps */
.progress-steps {
  display: flex;
  justify-content: space-between;
  position: relative;
  padding: 0 var(--space-4);
}

.progress-steps::before {
  content: "";
  position: absolute;
  top: 20px;
  left: var(--space-8);
  right: var(--space-8);
  height: 2px;
  background: var(--border-default);
}

.progress-step {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
}

.progress-step-indicator {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--surface-primary);
  border: 2px solid var(--border-default);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-semibold);
  transition: all 0.3s ease;
}

.progress-step.active .progress-step-indicator {
  background: var(--primary-600);
  border-color: var(--primary-600);
  color: white;
  transform: scale(1.1);
}

.progress-step.completed .progress-step-indicator {
  background: var(--success-500);
  border-color: var(--success-500);
  color: white;
}

/* Skeleton loading */
.skeleton-wave {
  position: relative;
  overflow: hidden;
}

.skeleton-wave::after {
  content: "";
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  transform: translateX(-100%);
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.4),
    transparent
  );
  animation: wave 1.5s linear infinite;
}

@keyframes wave {
  100% {
    transform: translateX(100%);
  }
}
```

## Scroll Interactions

### Smooth Scrolling
```css
/* Smooth scroll behavior */
html {
  scroll-behavior: smooth;
}

/* Scroll snap */
.scroll-snap-container {
  scroll-snap-type: x mandatory;
  overflow-x: auto;
  display: flex;
  gap: var(--space-4);
}

.scroll-snap-item {
  scroll-snap-align: start;
  flex: 0 0 300px;
}

/* Parallax scrolling */
.parallax-container {
  position: relative;
  overflow: hidden;
  height: 400px;
}

.parallax-bg {
  position: absolute;
  top: -20%;
  left: 0;
  width: 100%;
  height: 120%;
  background-size: cover;
  will-change: transform;
}

/* Reveal on scroll */
.reveal-on-scroll {
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease;
}

.reveal-on-scroll.revealed {
  opacity: 1;
  transform: translateY(0);
}

/* Sticky elements */
.sticky-nav {
  position: sticky;
  top: 0;
  z-index: 40;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;
}

.sticky-nav.scrolled {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
```

### Infinite Scroll
```css
/* Infinite scroll container */
.infinite-scroll {
  position: relative;
}

.infinite-scroll-loader {
  text-align: center;
  padding: var(--space-6);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.infinite-scroll.loading .infinite-scroll-loader {
  opacity: 1;
}

/* Load more button */
.load-more {
  width: 100%;
  padding: var(--space-4);
  margin-top: var(--space-6);
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.load-more:hover {
  background: var(--surface-tertiary);
  border-color: var(--border-strong);
}

.load-more.loading {
  pointer-events: none;
  color: transparent;
}
```

## Gestures & Touch

### Touch Interactions
```css
/* Touch feedback */
.touchable {
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
  user-select: none;
}

.touchable:active {
  transform: scale(0.98);
  opacity: 0.8;
}

/* Swipeable cards */
.swipeable {
  position: relative;
  touch-action: pan-y;
  user-select: none;
}

.swipeable.swiping {
  transition: none;
}

.swipeable.swipe-left {
  transform: translateX(-100%) rotate(-10deg);
  opacity: 0;
}

.swipeable.swipe-right {
  transform: translateX(100%) rotate(10deg);
  opacity: 0;
}

/* Pull to refresh */
.pull-to-refresh {
  position: relative;
  overflow: hidden;
}

.pull-to-refresh-indicator {
  position: absolute;
  top: -50px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 40px;
  opacity: 0;
  transition: all 0.3s ease;
}

.pull-to-refresh.pulling .pull-to-refresh-indicator {
  opacity: 1;
  transform: translateX(-50%) translateY(var(--pull-distance));
}

.pull-to-refresh.refreshing .pull-to-refresh-indicator {
  transform: translateX(-50%) translateY(60px);
  animation: spin 1s linear infinite;
}
```

## Micro-interactions

### Icon Animations
```css
/* Menu to close */
.menu-icon {
  width: 24px;
  height: 24px;
  position: relative;
  cursor: pointer;
}

.menu-icon span {
  position: absolute;
  height: 2px;
  width: 100%;
  background: currentColor;
  transition: all 0.3s ease;
}

.menu-icon span:nth-child(1) { top: 6px; }
.menu-icon span:nth-child(2) { top: 11px; }
.menu-icon span:nth-child(3) { top: 16px; }

.menu-icon.active span:nth-child(1) {
  transform: rotate(45deg);
  top: 11px;
}

.menu-icon.active span:nth-child(2) {
  opacity: 0;
}

.menu-icon.active span:nth-child(3) {
  transform: rotate(-45deg);
  top: 11px;
}

/* Heart animation */
.heart-icon {
  cursor: pointer;
  transition: all 0.3s ease;
}

.heart-icon:hover {
  transform: scale(1.1);
}

.heart-icon.active {
  color: var(--error-500);
  animation: heartbeat 0.6s ease;
}

@keyframes heartbeat {
  0% { transform: scale(1); }
  25% { transform: scale(1.3); }
  50% { transform: scale(1); }
  75% { transform: scale(1.3); }
  100% { transform: scale(1); }
}

/* Copy success */
.copy-button {
  position: relative;
}

.copy-button.copied::after {
  content: "Copied!";
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--gray-900);
  color: white;
  padding: var(--space-1) var(--space-2);
  border-radius: 4px;
  font-size: var(--text-xs);
  white-space: nowrap;
  animation: fadeInOut 2s ease;
}

@keyframes fadeInOut {
  0%, 100% { opacity: 0; transform: translateX(-50%) translateY(5px); }
  10%, 90% { opacity: 1; transform: translateX(-50%) translateY(0); }
}
```

## Feedback Patterns

### Tooltips
```css
/* Tooltip container */
.tooltip {
  position: relative;
  cursor: help;
}

.tooltip-content {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%) scale(0.8);
  background: var(--gray-900);
  color: white;
  padding: var(--space-1) var(--space-2);
  border-radius: 4px;
  font-size: var(--text-sm);
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: all 0.2s ease;
}

.tooltip:hover .tooltip-content {
  opacity: 1;
  transform: translateX(-50%) scale(1);
}

.tooltip-content::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 4px solid transparent;
  border-top-color: var(--gray-900);
}

/* Tooltip positions */
.tooltip-top .tooltip-content { 
  bottom: calc(100% + 8px); 
  top: auto;
}

.tooltip-bottom .tooltip-content { 
  top: calc(100% + 8px); 
  bottom: auto;
}

.tooltip-left .tooltip-content { 
  right: calc(100% + 8px); 
  left: auto;
  top: 50%;
  transform: translateY(-50%) scale(0.8);
}

.tooltip-right .tooltip-content { 
  left: calc(100% + 8px); 
  right: auto;
  top: 50%;
  transform: translateY(-50%) scale(0.8);
}
```

### Popovers
```css
/* Popover container */
.popover {
  position: relative;
}

.popover-content {
  position: absolute;
  top: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background: var(--surface-primary);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  padding: var(--space-3);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-width: 200px;
  max-width: 300px;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  z-index: 10;
}

.popover.active .popover-content {
  opacity: 1;
  visibility: visible;
}

/* Popover arrow */
.popover-content::before {
  content: "";
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 8px solid transparent;
  border-bottom-color: var(--border-default);
}

.popover-content::after {
  content: "";
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 7px solid transparent;
  border-bottom-color: var(--surface-primary);
}
```

## Performance Considerations

### Optimized Animations
```css
/* Use transform and opacity only */
.optimized-animation {
  will-change: transform, opacity;
  transform: translateZ(0); /* Force GPU layer */
}

/* Reduce motion preference */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Debounced interactions */
.debounced {
  transition: all 0.3s ease;
  transition-delay: 0.1s;
}

.debounced:hover {
  transition-delay: 0s;
}
```