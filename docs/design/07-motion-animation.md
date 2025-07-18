# Motion & Animation

## Motion Philosophy

### Core Principles
1. **Purposeful Motion**: Every animation serves a function
2. **Natural Physics**: Follow real-world motion principles
3. **Performance First**: 60fps minimum, no janky animations
4. **Subtle Enhancement**: Motion supports, never distracts
5. **Consistent Timing**: Unified duration and easing curves

## Animation Fundamentals

### Timing System
```css
:root {
  /* Duration scale */
  --duration-instant: 100ms;   /* Micro interactions */
  --duration-fast: 200ms;      /* Default transitions */
  --duration-normal: 300ms;    /* Standard animations */
  --duration-slow: 500ms;      /* Complex transitions */
  --duration-slower: 800ms;    /* Page transitions */
  --duration-slowest: 1000ms;  /* Dramatic reveals */
  
  /* Easing curves */
  --ease-linear: linear;
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
  
  /* Standard transitions */
  --transition-default: all var(--duration-fast) var(--ease-out);
  --transition-transform: transform var(--duration-fast) var(--ease-out);
  --transition-opacity: opacity var(--duration-fast) var(--ease-out);
  --transition-colors: color var(--duration-fast) var(--ease-out), 
                      background-color var(--duration-fast) var(--ease-out),
                      border-color var(--duration-fast) var(--ease-out);
}
```

### Performance Guidelines
```css
/* Performant properties */
.performant-animation {
  /* Only animate these properties */
  transform: translateX(0);
  opacity: 1;
  
  /* Force GPU acceleration */
  will-change: transform, opacity;
  transform: translateZ(0);
  backface-visibility: hidden;
  perspective: 1000px;
}

/* Avoid animating these */
.avoid-animation {
  /* Layout properties - cause reflow */
  width: auto;
  height: auto;
  padding: auto;
  margin: auto;
  
  /* Paint properties - cause repaint */
  background-color: auto;
  color: auto;
  box-shadow: auto;
}
```

## Transition Patterns

### Hover Transitions
```css
/* Standard hover */
.hover-transition {
  transition: var(--transition-default);
}

.hover-transition:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Directional hover */
.hover-from-left {
  position: relative;
  overflow: hidden;
}

.hover-from-left::before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: var(--primary-100);
  transition: left var(--duration-normal) var(--ease-out);
  z-index: -1;
}

.hover-from-left:hover::before {
  left: 0;
}

/* Morphing hover */
.hover-morph {
  border-radius: 8px;
  transition: border-radius var(--duration-normal) var(--ease-spring);
}

.hover-morph:hover {
  border-radius: 16px;
}
```

### State Transitions
```css
/* Toggle states */
.toggle-transition {
  transition: var(--transition-transform);
}

.toggle-transition.active {
  transform: rotate(180deg);
}

/* Multi-state transitions */
.multi-state {
  transition: all var(--duration-normal) var(--ease-out);
}

.multi-state.loading {
  opacity: 0.6;
  transform: scale(0.98);
}

.multi-state.success {
  background: var(--success-50);
  transform: scale(1.02);
}

.multi-state.error {
  background: var(--error-50);
  animation: shake var(--duration-fast) var(--ease-bounce);
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-8px); }
  75% { transform: translateX(8px); }
}
```

### Page Transitions
```css
/* Fade transition */
.page-fade-enter {
  opacity: 0;
}

.page-fade-enter-active {
  opacity: 1;
  transition: opacity var(--duration-slow) var(--ease-out);
}

.page-fade-exit {
  opacity: 1;
}

.page-fade-exit-active {
  opacity: 0;
  transition: opacity var(--duration-slow) var(--ease-out);
}

/* Slide transition */
.page-slide-enter {
  transform: translateX(100%);
}

.page-slide-enter-active {
  transform: translateX(0);
  transition: transform var(--duration-slow) var(--ease-out);
}

.page-slide-exit {
  transform: translateX(0);
}

.page-slide-exit-active {
  transform: translateX(-100%);
  transition: transform var(--duration-slow) var(--ease-out);
}

/* Scale transition */
.page-scale-enter {
  transform: scale(0.9);
  opacity: 0;
}

.page-scale-enter-active {
  transform: scale(1);
  opacity: 1;
  transition: all var(--duration-slow) var(--ease-out);
}
```

## Animation Patterns

### Entrance Animations
```css
/* Fade in */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.fade-in {
  animation: fadeIn var(--duration-normal) var(--ease-out);
}

/* Slide up */
@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.slide-up {
  animation: slideUp var(--duration-normal) var(--ease-out);
}

/* Scale in */
@keyframes scaleIn {
  from {
    transform: scale(0.9);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.scale-in {
  animation: scaleIn var(--duration-normal) var(--ease-out);
}

/* Rotate in */
@keyframes rotateIn {
  from {
    transform: rotate(-180deg) scale(0);
    opacity: 0;
  }
  to {
    transform: rotate(0) scale(1);
    opacity: 1;
  }
}

.rotate-in {
  animation: rotateIn var(--duration-slow) var(--ease-spring);
}
```

### Exit Animations
```css
/* Fade out */
@keyframes fadeOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}

.fade-out {
  animation: fadeOut var(--duration-normal) var(--ease-out);
}

/* Slide down */
@keyframes slideDown {
  from {
    transform: translateY(0);
    opacity: 1;
  }
  to {
    transform: translateY(20px);
    opacity: 0;
  }
}

.slide-down {
  animation: slideDown var(--duration-normal) var(--ease-out);
}

/* Scale out */
@keyframes scaleOut {
  from {
    transform: scale(1);
    opacity: 1;
  }
  to {
    transform: scale(0.9);
    opacity: 0;
  }
}

.scale-out {
  animation: scaleOut var(--duration-normal) var(--ease-out);
}

/* Collapse */
@keyframes collapse {
  from {
    max-height: var(--max-height, 1000px);
    opacity: 1;
  }
  to {
    max-height: 0;
    opacity: 0;
    padding: 0;
    margin: 0;
  }
}

.collapse {
  animation: collapse var(--duration-normal) var(--ease-out);
  overflow: hidden;
}
```

### Attention Animations
```css
/* Pulse */
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.pulse {
  animation: pulse var(--duration-slower) var(--ease-in-out) infinite;
}

/* Bounce */
@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-20px);
  }
  60% {
    transform: translateY(-10px);
  }
}

.bounce {
  animation: bounce var(--duration-slower) var(--ease-out);
}

/* Wiggle */
@keyframes wiggle {
  0%, 100% {
    transform: rotate(0deg);
  }
  25% {
    transform: rotate(-3deg);
  }
  75% {
    transform: rotate(3deg);
  }
}

.wiggle {
  animation: wiggle var(--duration-fast) var(--ease-in-out) 3;
}

/* Glow */
@keyframes glow {
  0%, 100% {
    box-shadow: 0 0 5px rgba(var(--primary-500-rgb), 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(var(--primary-500-rgb), 0.8);
  }
}

.glow {
  animation: glow var(--duration-slower) var(--ease-in-out) infinite;
}
```

### Loading Animations
```css
/* Spinner */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.spin {
  animation: spin var(--duration-slowest) var(--ease-linear) infinite;
}

/* Progress bar */
@keyframes progress {
  from {
    transform: translateX(-100%);
  }
  to {
    transform: translateX(0);
  }
}

.progress-bar {
  position: relative;
  overflow: hidden;
}

.progress-bar::after {
  content: "";
  position: absolute;
  inset: 0;
  background: var(--primary-600);
  transform: translateX(-100%);
  animation: progress var(--duration-slowest) var(--ease-out);
}

/* Skeleton pulse */
@keyframes skeleton-pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
  100% {
    opacity: 1;
  }
}

.skeleton-pulse {
  animation: skeleton-pulse var(--duration-slower) var(--ease-in-out) infinite;
}

/* Dots loading */
@keyframes dots {
  0%, 20% {
    transform: scale(0);
    opacity: 0;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
  80%, 100% {
    transform: scale(0);
    opacity: 0;
  }
}

.loading-dots span {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary-600);
  animation: dots var(--duration-slowest) var(--ease-out) infinite;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}
```

## Orchestrated Animations

### Staggered Animations
```css
/* Stagger children */
.stagger-children > * {
  animation: fadeIn var(--duration-normal) var(--ease-out) both;
}

.stagger-children > *:nth-child(1) { animation-delay: 0ms; }
.stagger-children > *:nth-child(2) { animation-delay: 50ms; }
.stagger-children > *:nth-child(3) { animation-delay: 100ms; }
.stagger-children > *:nth-child(4) { animation-delay: 150ms; }
.stagger-children > *:nth-child(5) { animation-delay: 200ms; }
.stagger-children > *:nth-child(6) { animation-delay: 250ms; }

/* Dynamic stagger with CSS variables */
.stagger-dynamic > * {
  animation: slideUp var(--duration-normal) var(--ease-out) both;
  animation-delay: calc(var(--stagger-delay, 50ms) * var(--index));
}
```

### Sequential Animations
```css
/* Chain animations */
@keyframes revealThenHighlight {
  0% {
    opacity: 0;
    transform: translateY(20px);
  }
  50% {
    opacity: 1;
    transform: translateY(0);
  }
  75% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 0 3px rgba(var(--primary-500-rgb), 0.5);
  }
}

.reveal-highlight {
  animation: revealThenHighlight var(--duration-slower) var(--ease-out);
}

/* Multi-step animation */
@keyframes multiStep {
  0% {
    transform: translateX(-100%) rotate(0deg);
    opacity: 0;
  }
  25% {
    transform: translateX(0) rotate(0deg);
    opacity: 1;
  }
  50% {
    transform: translateX(0) rotate(180deg);
  }
  75% {
    transform: translateX(0) rotate(180deg) scale(1.2);
  }
  100% {
    transform: translateX(0) rotate(360deg) scale(1);
  }
}

.multi-step {
  animation: multiStep var(--duration-slowest) var(--ease-out);
}
```

### Coordinated Animations
```css
/* Parent-child coordination */
.coordinated-parent {
  animation: scaleIn var(--duration-normal) var(--ease-out);
}

.coordinated-parent .child {
  animation: fadeIn var(--duration-normal) var(--ease-out);
  animation-delay: var(--duration-fast);
}

/* Synchronized elements */
.sync-group > * {
  animation-duration: var(--duration-slow);
  animation-timing-function: var(--ease-out);
  animation-fill-mode: both;
}

.sync-group .primary {
  animation-name: slideUp;
}

.sync-group .secondary {
  animation-name: fadeIn;
  animation-delay: var(--duration-instant);
}

.sync-group .tertiary {
  animation-name: scaleIn;
  animation-delay: calc(var(--duration-instant) * 2);
}
```

## Gesture Animations

### Swipe Animations
```css
/* Swipe to dismiss */
@keyframes swipeOut {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}

.swipe-dismiss {
  animation: swipeOut var(--duration-normal) var(--ease-out);
}

/* Swipe reveal */
.swipe-reveal {
  position: relative;
  overflow: hidden;
}

.swipe-reveal-content {
  transform: translateX(0);
  transition: transform var(--duration-normal) var(--ease-out);
}

.swipe-reveal.swiped .swipe-reveal-content {
  transform: translateX(-80px);
}

.swipe-reveal-actions {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: 0 var(--space-3);
  transform: translateX(100%);
  transition: transform var(--duration-normal) var(--ease-out);
}

.swipe-reveal.swiped .swipe-reveal-actions {
  transform: translateX(0);
}
```

### Pinch & Zoom
```css
/* Zoomable content */
.zoomable {
  transition: transform var(--duration-normal) var(--ease-out);
  transform-origin: center center;
}

.zoomable.zooming {
  transition: none;
}

.zoomable.zoomed {
  transform: scale(var(--zoom-scale, 2));
}

/* Lightbox effect */
@keyframes lightboxOpen {
  from {
    transform: scale(var(--initial-scale, 1));
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.lightbox {
  animation: lightboxOpen var(--duration-normal) var(--ease-out);
}
```

## Physics-Based Motion

### Spring Physics
```css
/* Spring animation */
@keyframes springBounce {
  0% {
    transform: scale(1);
  }
  30% {
    transform: scale(1.25);
  }
  40% {
    transform: scale(0.75);
  }
  50% {
    transform: scale(1.15);
  }
  65% {
    transform: scale(0.95);
  }
  75% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

.spring-bounce {
  animation: springBounce var(--duration-slower) linear;
}

/* Elastic effect */
@keyframes elastic {
  0% {
    transform: scale(1);
  }
  30% {
    transform: scale(1.25);
  }
  40% {
    transform: scale(0.75);
  }
  50% {
    transform: scale(1.15);
  }
  65% {
    transform: scale(0.95);
  }
  75% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

.elastic {
  animation: elastic var(--duration-slowest) var(--ease-linear);
}
```

### Momentum Scrolling
```css
/* Smooth momentum scroll */
.momentum-scroll {
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  scroll-behavior: smooth;
}

/* Scroll snap with momentum */
.momentum-snap {
  scroll-snap-type: y mandatory;
  scroll-padding: var(--space-4);
}

.momentum-snap > * {
  scroll-snap-align: start;
  scroll-snap-stop: always;
}

/* Parallax with momentum */
.parallax-container {
  perspective: 1px;
  overflow-y: auto;
  overflow-x: hidden;
}

.parallax-layer {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.parallax-layer-base {
  transform: translateZ(0);
}

.parallax-layer-back {
  transform: translateZ(-1px) scale(2);
}
```

## Animation Utilities

### Animation Controls
```css
/* Play states */
.animation-play { animation-play-state: running; }
.animation-pause { animation-play-state: paused; }

/* Fill modes */
.animation-fill-none { animation-fill-mode: none; }
.animation-fill-forwards { animation-fill-mode: forwards; }
.animation-fill-backwards { animation-fill-mode: backwards; }
.animation-fill-both { animation-fill-mode: both; }

/* Iteration */
.animation-once { animation-iteration-count: 1; }
.animation-twice { animation-iteration-count: 2; }
.animation-infinite { animation-iteration-count: infinite; }

/* Direction */
.animation-normal { animation-direction: normal; }
.animation-reverse { animation-direction: reverse; }
.animation-alternate { animation-direction: alternate; }
.animation-alternate-reverse { animation-direction: alternate-reverse; }
```

### Performance Optimization
```css
/* Reduce motion preference */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* GPU acceleration hints */
.gpu-accelerated {
  transform: translateZ(0);
  will-change: transform;
  backface-visibility: hidden;
  perspective: 1000px;
}

/* Remove after animation */
.animation-cleanup {
  animation: slideUp var(--duration-normal) var(--ease-out);
}

.animation-cleanup[data-animation-complete="true"] {
  animation: none;
  will-change: auto;
}
```