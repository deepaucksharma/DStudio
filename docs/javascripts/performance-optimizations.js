// Performance Optimizations for Mobile
class PerformanceOptimizer {
  constructor() {
    this.isMobile = window.innerWidth <= 768 || ('ontouchstart' in window);
    this.rafCallbacks = new Map();
    this.scrollHandlers = new Map();
    this.resizeHandlers = new Map();
    this.init();
  }
  
  init() {
    if (this.isMobile) {
      this.optimizeScrollHandlers();
      this.optimizeResizeHandlers();
      this.optimizeAnimations();
      this.reduceRepaints();
      this.optimizeTouchHandlers();
    }
    
    // Apply optimizations regardless of device
    this.enablePassiveListeners();
    this.deferNonCriticalJS();
    this.optimizeImages();
  }
  
  // Consolidate all scroll handlers into one
  optimizeScrollHandlers() {
    let ticking = false;
    let lastScrollY = 0;
    const scrollCallbacks = [];
    
    // Override addEventListener for scroll events
    const originalAddEventListener = window.addEventListener;
    window.addEventListener = function(type, handler, options) {
      if (type === 'scroll') {
        scrollCallbacks.push(handler);
        return;
      }
      return originalAddEventListener.call(this, type, handler, options);
    };
    
    // Single optimized scroll handler
    const handleScroll = () => {
      lastScrollY = window.scrollY;
      
      if (!ticking) {
        window.requestAnimationFrame(() => {
          // Execute all scroll callbacks
          scrollCallbacks.forEach(callback => {
            try {
              callback({ target: window });
            } catch (e) {
              console.error('Scroll handler error:', e);
            }
          });
          ticking = false;
        });
        ticking = true;
      }
    };
    
    // Use passive listener for better performance
    originalAddEventListener.call(window, 'scroll', handleScroll, { passive: true });
  }
  
  // Debounce resize handlers
  optimizeResizeHandlers() {
    let resizeTimeout;
    const resizeCallbacks = [];
    
    // Override addEventListener for resize events
    const originalAddEventListener = window.addEventListener;
    window.addEventListener = function(type, handler, options) {
      if (type === 'resize' || type === 'orientationchange') {
        resizeCallbacks.push(handler);
        return;
      }
      return originalAddEventListener.apply(this, arguments);
    };
    
    // Debounced resize handler
    const handleResize = () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        resizeCallbacks.forEach(callback => {
          try {
            callback({ target: window });
          } catch (e) {
            console.error('Resize handler error:', e);
          }
        });
      }, 250); // Debounce by 250ms
    };
    
    originalAddEventListener.call(window, 'resize', handleResize, { passive: true });
    originalAddEventListener.call(window, 'orientationchange', handleResize, { passive: true });
  }
  
  // Optimize animations on mobile
  optimizeAnimations() {
    if (this.isMobile) {
      // Reduce animation durations
      const style = document.createElement('style');
      style.textContent = `
        @media (max-width: 768px) {
          *, *::before, *::after {
            animation-duration: 0.2s !important;
            transition-duration: 0.2s !important;
          }
          
          /* Disable non-essential animations */
          .hero-animation,
          .journey-map svg .node,
          .axiom-box,
          .concept-card {
            animation: none !important;
          }
          
          /* Use transform for animations instead of position */
          .reading-progress,
          .mobile-bottom-nav,
          .command-palette {
            will-change: transform;
          }
        }
        
        /* Use GPU acceleration for specific elements */
        .reading-progress-fill,
        .hero-animation canvas,
        .journey-map svg {
          transform: translateZ(0);
          will-change: transform;
        }
      `;
      document.head.appendChild(style);
    }
  }
  
  // Reduce repaints and reflows
  reduceRepaints() {
    // Batch DOM reads and writes
    const readQueue = [];
    const writeQueue = [];
    
    window.batchRead = (fn) => {
      readQueue.push(fn);
      scheduleFlush();
    };
    
    window.batchWrite = (fn) => {
      writeQueue.push(fn);
      scheduleFlush();
    };
    
    let scheduled = false;
    const scheduleFlush = () => {
      if (!scheduled) {
        scheduled = true;
        requestAnimationFrame(flush);
      }
    };
    
    const flush = () => {
      // Execute all reads first
      const reads = readQueue.splice(0);
      reads.forEach(fn => fn());
      
      // Then execute all writes
      const writes = writeQueue.splice(0);
      writes.forEach(fn => fn());
      
      scheduled = false;
    };
  }
  
  // Optimize touch handlers
  optimizeTouchHandlers() {
    // Prevent overscroll on iOS
    document.body.style.overscrollBehavior = 'none';
    
    // Add touch-action CSS for better performance
    const style = document.createElement('style');
    style.textContent = `
      /* Optimize touch performance */
      .swipeable {
        touch-action: pan-y;
      }
      
      .no-swipe {
        touch-action: none;
      }
      
      .md-content__inner {
        touch-action: pan-y;
      }
      
      button, a, .clickable {
        touch-action: manipulation;
      }
      
      /* Disable touch delay */
      * {
        -webkit-tap-highlight-color: transparent;
      }
    `;
    document.head.appendChild(style);
  }
  
  // Enable passive event listeners globally
  enablePassiveListeners() {
    // Override addEventListener to use passive by default for touch/wheel events
    const originalAddEventListener = EventTarget.prototype.addEventListener;
    EventTarget.prototype.addEventListener = function(type, handler, options) {
      if (typeof options === 'boolean') {
        options = { capture: options };
      } else if (!options) {
        options = {};
      }
      
      // Make touch and wheel events passive by default
      if (['touchstart', 'touchmove', 'wheel', 'mousewheel'].includes(type)) {
        if (options.passive === undefined) {
          options.passive = true;
        }
      }
      
      return originalAddEventListener.call(this, type, handler, options);
    };
  }
  
  // Defer non-critical JavaScript
  deferNonCriticalJS() {
    // List of non-critical scripts that can be deferred
    const nonCriticalScripts = [
      'tooltips-help.js',
      'consistency-visualizer.js',
      'cap-explorer.js',
      'capacity-planner.js'
    ];
    
    // Find and defer these scripts
    document.querySelectorAll('script').forEach(script => {
      const src = script.src;
      if (src && nonCriticalScripts.some(name => src.includes(name))) {
        script.setAttribute('defer', '');
      }
    });
  }
  
  // Optimize images
  optimizeImages() {
    // Add loading="lazy" to all images
    document.querySelectorAll('img').forEach(img => {
      if (!img.loading) {
        img.loading = 'lazy';
      }
      
      // Add decoding="async" for better performance
      if (!img.decoding) {
        img.decoding = 'async';
      }
    });
    
    // Use Intersection Observer for images in viewport
    if ('IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            // Preload image
            if (img.dataset.src) {
              img.src = img.dataset.src;
              img.removeAttribute('data-src');
              imageObserver.unobserve(img);
            }
          }
        });
      }, {
        rootMargin: '50px'
      });
      
      // Observe all images with data-src
      document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
      });
    }
  }
  
  // Utility method to throttle functions
  static throttle(func, limit) {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }
  
  // Utility method to debounce functions
  static debounce(func, wait) {
    let timeout;
    return function() {
      const context = this;
      const args = arguments;
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(context, args), wait);
    };
  }
}

// Initialize performance optimizations early
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new PerformanceOptimizer());
} else {
  new PerformanceOptimizer();
}

// Export for use in other scripts
window.PerformanceOptimizer = PerformanceOptimizer;