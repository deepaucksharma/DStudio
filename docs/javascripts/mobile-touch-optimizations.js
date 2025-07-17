// Mobile Touch Optimizations
class MobileTouchOptimizations {
  constructor() {
    this.init();
  }
  
  init() {
    if (this.isTouchDevice()) {
      this.optimizeTouchTargets();
      this.addTouchFeedback();
      this.preventDoubleTapZoom();
      this.improveScrollPerformance();
      this.optimizeFormInputs();
      this.addPullToRefresh();
    }
  }
  
  isTouchDevice() {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  }
  
  optimizeTouchTargets() {
    // Minimum touch target size (44x44px - iOS HIG)
    const MIN_SIZE = 44;
    
    // Find all interactive elements
    const interactiveSelectors = [
      'a', 'button', 'input', 'select', 'textarea',
      '[role="button"]', '[tabindex]:not([tabindex="-1"])',
      '.md-nav__link', '.md-tabs__link', '.md-search__input',
      '.concept-card', '.journey-card', '.tool-button'
    ];
    
    const elements = document.querySelectorAll(interactiveSelectors.join(','));
    
    elements.forEach(element => {
      // Skip if already optimized
      if (element.hasAttribute('data-touch-optimized')) return;
      
      const rect = element.getBoundingClientRect();
      const computedStyle = window.getComputedStyle(element);
      
      // Check current size
      const width = rect.width;
      const height = rect.height;
      
      // Add padding if needed to meet minimum size
      if (width < MIN_SIZE || height < MIN_SIZE) {
        const currentPaddingH = parseFloat(computedStyle.paddingLeft) + parseFloat(computedStyle.paddingRight);
        const currentPaddingV = parseFloat(computedStyle.paddingTop) + parseFloat(computedStyle.paddingBottom);
        
        const neededPaddingH = Math.max(0, (MIN_SIZE - width + currentPaddingH) / 2);
        const neededPaddingV = Math.max(0, (MIN_SIZE - height + currentPaddingV) / 2);
        
        if (neededPaddingH > 0) {
          element.style.paddingLeft = `${parseFloat(computedStyle.paddingLeft) + neededPaddingH}px`;
          element.style.paddingRight = `${parseFloat(computedStyle.paddingRight) + neededPaddingH}px`;
        }
        
        if (neededPaddingV > 0) {
          element.style.paddingTop = `${parseFloat(computedStyle.paddingTop) + neededPaddingV}px`;
          element.style.paddingBottom = `${parseFloat(computedStyle.paddingBottom) + neededPaddingV}px`;
        }
      }
      
      // Add touch optimization attributes
      element.setAttribute('data-touch-optimized', 'true');
      
      // Improve touch accuracy for small text links
      if (element.tagName === 'A' && width < MIN_SIZE * 1.5) {
        this.addTouchExpander(element);
      }
    });
  }
  
  addTouchExpander(element) {
    // Create invisible touch target expander
    const expander = document.createElement('span');
    expander.className = 'touch-expander';
    expander.setAttribute('aria-hidden', 'true');
    
    // Position expander
    element.style.position = 'relative';
    element.appendChild(expander);
    
    // Forward touch events
    expander.addEventListener('click', (e) => {
      e.stopPropagation();
      element.click();
    });
  }
  
  addTouchFeedback() {
    // Visual feedback for touch interactions
    document.addEventListener('touchstart', (e) => {
      const target = e.target.closest('a, button, [role="button"], .touchable');
      if (target) {
        target.classList.add('touch-active');
        target.setAttribute('data-touch-start', Date.now());
      }
    }, { passive: true });
    
    document.addEventListener('touchend', (e) => {
      const target = e.target.closest('.touch-active');
      if (target) {
        const touchDuration = Date.now() - parseInt(target.getAttribute('data-touch-start') || 0);
        const minDuration = 100;
        
        // Ensure feedback is visible for minimum duration
        if (touchDuration < minDuration) {
          setTimeout(() => {
            target.classList.remove('touch-active');
          }, minDuration - touchDuration);
        } else {
          target.classList.remove('touch-active');
        }
      }
    }, { passive: true });
    
    // Handle touch cancel
    document.addEventListener('touchcancel', (e) => {
      document.querySelectorAll('.touch-active').forEach(element => {
        element.classList.remove('touch-active');
      });
    }, { passive: true });
  }
  
  preventDoubleTapZoom() {
    // Prevent double-tap zoom on buttons and links
    let lastTap = 0;
    
    document.addEventListener('touchend', (e) => {
      const target = e.target.closest('button, a, [role="button"]');
      if (!target) return;
      
      const currentTime = Date.now();
      const tapLength = currentTime - lastTap;
      
      if (tapLength < 500 && tapLength > 0) {
        e.preventDefault();
        // Trigger click if it's a genuine double-tap
        target.click();
      }
      
      lastTap = currentTime;
    });
  }
  
  improveScrollPerformance() {
    // Add momentum scrolling to scrollable containers
    const scrollContainers = document.querySelectorAll(
      '.md-sidebar__scrollwrap, .md-content__inner, .tool-results, pre, .overflow-auto'
    );
    
    scrollContainers.forEach(container => {
      // Enable momentum scrolling on iOS
      container.style.webkitOverflowScrolling = 'touch';
      
      // Add scroll indicators
      this.addScrollIndicators(container);
      
      // Optimize scroll performance
      container.addEventListener('scroll', this.throttle(() => {
        this.updateScrollIndicators(container);
      }, 100), { passive: true });
    });
  }
  
  addScrollIndicators(container) {
    // Skip if already has indicators
    if (container.querySelector('.scroll-indicator')) return;
    
    const wrapper = document.createElement('div');
    wrapper.className = 'scroll-indicator-wrapper';
    
    const topIndicator = document.createElement('div');
    topIndicator.className = 'scroll-indicator scroll-indicator-top';
    
    const bottomIndicator = document.createElement('div');
    bottomIndicator.className = 'scroll-indicator scroll-indicator-bottom';
    
    container.style.position = 'relative';
    container.appendChild(topIndicator);
    container.appendChild(bottomIndicator);
    
    // Initial state
    this.updateScrollIndicators(container);
  }
  
  updateScrollIndicators(container) {
    const topIndicator = container.querySelector('.scroll-indicator-top');
    const bottomIndicator = container.querySelector('.scroll-indicator-bottom');
    
    if (!topIndicator || !bottomIndicator) return;
    
    const scrollTop = container.scrollTop;
    const scrollHeight = container.scrollHeight;
    const clientHeight = container.clientHeight;
    const maxScroll = scrollHeight - clientHeight;
    
    // Show/hide indicators
    topIndicator.style.opacity = scrollTop > 10 ? '1' : '0';
    bottomIndicator.style.opacity = scrollTop < maxScroll - 10 ? '1' : '0';
  }
  
  optimizeFormInputs() {
    // Optimize form inputs for mobile
    const inputs = document.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
      // Prevent zoom on focus (iOS)
      if (input.type === 'text' || input.type === 'email' || input.type === 'number' || input.tagName === 'TEXTAREA') {
        const fontSize = window.getComputedStyle(input).fontSize;
        if (parseInt(fontSize) < 16) {
          input.style.fontSize = '16px';
        }
      }
      
      // Add input mode attributes
      if (input.type === 'number') {
        input.inputMode = 'numeric';
      } else if (input.type === 'email') {
        input.inputMode = 'email';
      } else if (input.type === 'url') {
        input.inputMode = 'url';
      } else if (input.type === 'tel') {
        input.inputMode = 'tel';
      }
      
      // Improve label touch targets
      const label = input.labels?.[0] || input.closest('label');
      if (label) {
        label.classList.add('touch-optimized-label');
      }
      
      // Auto-capitalize and auto-correct attributes
      if (input.type === 'text' && !input.hasAttribute('autocapitalize')) {
        input.autocapitalize = 'sentences';
      }
    });
  }
  
  addPullToRefresh() {
    // Custom pull-to-refresh implementation
    let startY = 0;
    let currentY = 0;
    let pulling = false;
    const threshold = 100;
    
    // Create pull indicator
    const pullIndicator = document.createElement('div');
    pullIndicator.className = 'pull-to-refresh';
    pullIndicator.innerHTML = `
      <div class="pull-to-refresh-icon">↓</div>
      <div class="pull-to-refresh-text">Pull to refresh</div>
    `;
    document.body.appendChild(pullIndicator);
    
    // Only enable on main content
    const content = document.querySelector('.md-content');
    if (!content) return;
    
    content.addEventListener('touchstart', (e) => {
      if (window.scrollY === 0) {
        startY = e.touches[0].clientY;
        pulling = true;
      }
    }, { passive: true });
    
    content.addEventListener('touchmove', (e) => {
      if (!pulling) return;
      
      currentY = e.touches[0].clientY;
      const pullDistance = currentY - startY;
      
      if (pullDistance > 0 && window.scrollY === 0) {
        e.preventDefault();
        
        const progress = Math.min(pullDistance / threshold, 1);
        const opacity = progress;
        const scale = 0.8 + (0.2 * progress);
        const translateY = Math.min(pullDistance * 0.5, 60);
        
        pullIndicator.style.opacity = opacity;
        pullIndicator.style.transform = `translateY(${translateY}px) scale(${scale})`;
        
        if (pullDistance > threshold) {
          pullIndicator.querySelector('.pull-to-refresh-text').textContent = 'Release to refresh';
          pullIndicator.classList.add('ready');
        } else {
          pullIndicator.querySelector('.pull-to-refresh-text').textContent = 'Pull to refresh';
          pullIndicator.classList.remove('ready');
        }
      }
    });
    
    content.addEventListener('touchend', () => {
      if (!pulling) return;
      
      const pullDistance = currentY - startY;
      
      if (pullDistance > threshold && window.scrollY === 0) {
        // Trigger refresh
        pullIndicator.classList.add('refreshing');
        pullIndicator.querySelector('.pull-to-refresh-text').textContent = 'Refreshing...';
        
        // Simulate refresh
        setTimeout(() => {
          window.location.reload();
        }, 1000);
      } else {
        // Reset
        pullIndicator.style.opacity = '0';
        pullIndicator.style.transform = 'translateY(0) scale(0.8)';
      }
      
      pulling = false;
      startY = 0;
      currentY = 0;
    });
  }
  
  throttle(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
}

// Device-specific optimizations
class DeviceOptimizations {
  constructor() {
    this.detectDevice();
    this.applyOptimizations();
  }
  
  detectDevice() {
    const ua = navigator.userAgent.toLowerCase();
    
    this.isIOS = /iphone|ipad|ipod/.test(ua);
    this.isAndroid = /android/.test(ua);
    this.isSafari = /safari/.test(ua) && !/chrome/.test(ua);
    this.isChrome = /chrome/.test(ua) && !/edge/.test(ua);
    
    // Add device classes
    if (this.isIOS) document.body.classList.add('ios-device');
    if (this.isAndroid) document.body.classList.add('android-device');
    if (this.isSafari) document.body.classList.add('safari-browser');
    if (this.isChrome) document.body.classList.add('chrome-browser');
  }
  
  applyOptimizations() {
    if (this.isIOS) {
      this.applyIOSOptimizations();
    }
    
    if (this.isAndroid) {
      this.applyAndroidOptimizations();
    }
  }
  
  applyIOSOptimizations() {
    // Fix iOS rubber band scrolling
    document.body.addEventListener('touchmove', (e) => {
      if (e.target.closest('.md-sidebar__scrollwrap, .md-content__inner')) {
        return; // Allow scrolling in these containers
      }
      
      if (e.target === document.body && e.cancelable) {
        e.preventDefault();
      }
    }, { passive: false });
    
    // Fix iOS viewport height
    this.fixIOSViewportHeight();
    
    // Handle iOS keyboard
    this.handleIOSKeyboard();
  }
  
  fixIOSViewportHeight() {
    const setViewportHeight = () => {
      const vh = window.innerHeight * 0.01;
      document.documentElement.style.setProperty('--vh', `${vh}px`);
    };
    
    setViewportHeight();
    window.addEventListener('resize', setViewportHeight);
    window.addEventListener('orientationchange', setViewportHeight);
  }
  
  handleIOSKeyboard() {
    const inputs = document.querySelectorAll('input, textarea');
    
    inputs.forEach(input => {
      input.addEventListener('focus', () => {
        document.body.classList.add('keyboard-open');
        
        // Scroll input into view
        setTimeout(() => {
          input.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 300);
      });
      
      input.addEventListener('blur', () => {
        document.body.classList.remove('keyboard-open');
        window.scrollTo(0, 0); // Reset scroll position
      });
    });
  }
  
  applyAndroidOptimizations() {
    // Android-specific optimizations
    // Address bar hiding
    window.addEventListener('scroll', () => {
      if (window.scrollY > 100) {
        document.body.classList.add('scrolled');
      } else {
        document.body.classList.remove('scrolled');
      }
    });
  }
}

// Initialize optimizations
document.addEventListener('DOMContentLoaded', () => {
  new MobileTouchOptimizations();
  new DeviceOptimizations();
});