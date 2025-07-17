// Animation Performance Improvements
class AnimationPerformance {
  constructor() {
    this.animatedElements = new Set();
    this.init();
  }
  
  init() {
    // Reduce all animation durations to 200ms
    this.optimizeAnimationDurations();
    
    // Set up intersection observer for one-time animations
    this.setupOneTimeAnimations();
    
    // Disable animations for users who prefer reduced motion
    this.respectReducedMotion();
  }
  
  optimizeAnimationDurations() {
    // Create style element to override animation durations
    const style = document.createElement('style');
    style.textContent = `
      /* Override all animations to 200ms for better performance */
      *, *::before, *::after {
        animation-duration: 200ms !important;
        transition-duration: 200ms !important;
      }
      
      /* Exception for specific animations that need longer duration */
      .hero-animation canvas,
      #network-visualization {
        animation-duration: inherit !important;
      }
      
      /* Disable repetitive animations after first play */
      .animate-once {
        animation-iteration-count: 1 !important;
      }
    `;
    document.head.appendChild(style);
  }
  
  setupOneTimeAnimations() {
    // Find all elements with animation classes
    const animatedSelectors = [
      '.axiom-box',
      '.decision-box',
      '.failure-vignette',
      '.hero-content',
      '.stat-item',
      '.journey-card',
      '.concept-card'
    ];
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !this.animatedElements.has(entry.target)) {
          // Add animate-once class to ensure animation only plays once
          entry.target.classList.add('animate-once', 'animate-in-view');
          this.animatedElements.add(entry.target);
          
          // Stop observing this element
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '50px'
    });
    
    // Observe all animated elements
    animatedSelectors.forEach(selector => {
      document.querySelectorAll(selector).forEach(element => {
        // Remove any existing animation classes
        element.style.animationPlayState = 'paused';
        observer.observe(element);
      });
    });
  }
  
  respectReducedMotion() {
    // Check if user prefers reduced motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    
    const handleReducedMotion = () => {
      if (prefersReducedMotion.matches) {
        // Disable all animations
        const style = document.createElement('style');
        style.textContent = `
          *, *::before, *::after {
            animation: none !important;
            transition: none !important;
          }
        `;
        style.id = 'reduced-motion-styles';
        document.head.appendChild(style);
      } else {
        // Re-enable animations
        const reducedMotionStyles = document.getElementById('reduced-motion-styles');
        if (reducedMotionStyles) {
          reducedMotionStyles.remove();
        }
      }
    };
    
    // Initial check
    handleReducedMotion();
    
    // Listen for changes
    prefersReducedMotion.addEventListener('change', handleReducedMotion);
  }
}

// Initialize animation performance improvements
document.addEventListener('DOMContentLoaded', () => {
  new AnimationPerformance();
});