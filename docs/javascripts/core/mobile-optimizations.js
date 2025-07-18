/* ===================================
   Consolidated Mobile Optimizations
   Combines mobile navigation and touch optimizations
   =================================== */

class MobileOptimizations {
  constructor() {
    this.isMobile = this.detectMobile();
    this.touchStartX = 0;
    this.touchStartY = 0;
    this.swipeThreshold = 50;
    
    if (this.isMobile) {
      this.init();
    }
  }
  
  detectMobile() {
    return window.matchMedia('(max-width: 768px)').matches ||
           'ontouchstart' in window ||
           navigator.maxTouchPoints > 0;
  }
  
  init() {
    // Add mobile class to body
    document.body.classList.add('mobile-device');
    
    // Initialize all mobile optimizations
    this.setupMobileNavigation();
    this.optimizeTouchTargets();
    this.setupSwipeGestures();
    this.optimizeScrolling();
    this.setupViewportMeta();
    this.preventDoubleTap();
    this.optimizeImages();
    this.setupOrientationHandler();
  }
  
  setupMobileNavigation() {
    const hamburger = document.querySelector('.md-header__button');
    const nav = document.querySelector('.md-nav--primary');
    const overlay = this.createOverlay();
    
    if (hamburger && nav) {
      hamburger.addEventListener('click', (e) => {
        e.preventDefault();
        this.toggleMobileMenu();
      });
      
      // Close menu when clicking overlay
      overlay.addEventListener('click', () => {
        this.closeMobileMenu();
      });
      
      // Close menu on escape key
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && nav.classList.contains('md-nav--open')) {
          this.closeMobileMenu();
        }
      });
    }
  }
  
  createOverlay() {
    const overlay = document.createElement('div');
    overlay.className = 'md-overlay';
    document.body.appendChild(overlay);
    return overlay;
  }
  
  toggleMobileMenu() {
    const nav = document.querySelector('.md-nav--primary');
    const overlay = document.querySelector('.md-overlay');
    const isOpen = nav.classList.contains('md-nav--open');
    
    if (isOpen) {
      this.closeMobileMenu();
    } else {
      this.openMobileMenu();
    }
  }
  
  openMobileMenu() {
    const nav = document.querySelector('.md-nav--primary');
    const overlay = document.querySelector('.md-overlay');
    
    nav.classList.add('md-nav--open');
    overlay.classList.add('md-overlay--active');
    document.body.style.overflow = 'hidden';
    
    // Announce to screen readers
    nav.setAttribute('aria-expanded', 'true');
  }
  
  closeMobileMenu() {
    const nav = document.querySelector('.md-nav--primary');
    const overlay = document.querySelector('.md-overlay');
    
    nav.classList.remove('md-nav--open');
    overlay.classList.remove('md-overlay--active');
    document.body.style.overflow = '';
    
    // Announce to screen readers
    nav.setAttribute('aria-expanded', 'false');
  }
  
  optimizeTouchTargets() {
    // Ensure all interactive elements meet minimum touch target size
    const minSize = 44; // iOS recommendation
    const interactiveElements = document.querySelectorAll(
      'a, button, input, select, textarea, .md-nav__link, .md-tabs__link'
    );
    
    interactiveElements.forEach(element => {
      const rect = element.getBoundingClientRect();
      if (rect.height < minSize || rect.width < minSize) {
        element.style.minHeight = `${minSize}px`;
        element.style.minWidth = `${minSize}px`;
        element.style.display = 'inline-flex';
        element.style.alignItems = 'center';
        element.style.justifyContent = 'center';
      }
    });
  }
  
  setupSwipeGestures() {
    const content = document.querySelector('.md-content');
    if (!content) return;
    
    content.addEventListener('touchstart', (e) => {
      this.touchStartX = e.touches[0].clientX;
      this.touchStartY = e.touches[0].clientY;
    }, { passive: true });
    
    content.addEventListener('touchend', (e) => {
      const touchEndX = e.changedTouches[0].clientX;
      const touchEndY = e.changedTouches[0].clientY;
      
      const swipeX = touchEndX - this.touchStartX;
      const swipeY = Math.abs(touchEndY - this.touchStartY);
      
      // Horizontal swipe detection (ensure it's more horizontal than vertical)
      if (Math.abs(swipeX) > this.swipeThreshold && Math.abs(swipeX) > swipeY) {
        if (swipeX > 0) {
          // Swipe right - open menu
          this.openMobileMenu();
        } else {
          // Swipe left - close menu
          this.closeMobileMenu();
        }
      }
    }, { passive: true });
  }
  
  optimizeScrolling() {
    // Add momentum scrolling to scrollable areas
    const scrollableElements = document.querySelectorAll(
      '.md-sidebar__scrollwrap, .md-content, pre, .tabbed-content'
    );
    
    scrollableElements.forEach(element => {
      element.style.webkitOverflowScrolling = 'touch';
      element.style.overflowY = 'auto';
    });
    
    // Prevent scroll chaining
    document.addEventListener('touchmove', (e) => {
      if (e.target.closest('.md-nav--primary')) {
        e.stopPropagation();
      }
    }, { passive: false });
  }
  
  setupViewportMeta() {
    let viewport = document.querySelector('meta[name="viewport"]');
    if (!viewport) {
      viewport = document.createElement('meta');
      viewport.name = 'viewport';
      document.head.appendChild(viewport);
    }
    viewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes';
  }
  
  preventDoubleTap() {
    let lastTap = 0;
    document.addEventListener('touchend', (e) => {
      const currentTime = new Date().getTime();
      const tapLength = currentTime - lastTap;
      if (tapLength < 500 && tapLength > 0) {
        e.preventDefault();
      }
      lastTap = currentTime;
    }, { passive: false });
  }
  
  optimizeImages() {
    // Lazy load images on mobile
    if ('IntersectionObserver' in window) {
      const images = document.querySelectorAll('img[data-src]');
      const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
            imageObserver.unobserve(img);
          }
        });
      });
      
      images.forEach(img => imageObserver.observe(img));
    }
    
    // Set appropriate image sizes for mobile
    const contentImages = document.querySelectorAll('.md-content img');
    contentImages.forEach(img => {
      if (!img.hasAttribute('loading')) {
        img.loading = 'lazy';
      }
    });
  }
  
  setupOrientationHandler() {
    const handleOrientation = () => {
      const isLandscape = window.matchMedia('(orientation: landscape)').matches;
      document.body.classList.toggle('landscape-mode', isLandscape);
      
      // Adjust header height in landscape
      if (isLandscape && this.isMobile) {
        document.documentElement.style.setProperty('--md-header-height', '2.5rem');
      } else {
        document.documentElement.style.setProperty('--md-header-height', '3rem');
      }
    };
    
    window.addEventListener('orientationchange', handleOrientation);
    window.addEventListener('resize', handleOrientation);
    handleOrientation(); // Initial check
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new MobileOptimizations());
} else {
  new MobileOptimizations();
}