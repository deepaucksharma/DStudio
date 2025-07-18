// Mobile Navigation with Bottom Tabs and Swipe Gestures
class MobileNavigation {
  constructor() {
    this.touchStartX = 0;
    this.touchStartY = 0;
    this.touchEndX = 0;
    this.touchEndY = 0;
    this.swipeThreshold = 50;
    this.velocityThreshold = 0.3;
    this.touchStartTime = 0;
    this.isScrolling = false;
    
    if (this.isMobile()) {
      this.init();
    }
  }
  
  init() {
    this.createBottomNavigation();
    this.setupSwipeGestures();
    this.optimizeTouchTargets();
    this.addMobileOptimizations();
    this.setupOrientationHandler();
  }
  
  isMobile() {
    return window.innerWidth <= 768 || ('ontouchstart' in window);
  }
  
  createBottomNavigation() {
    // Create bottom navigation container
    const bottomNav = document.createElement('nav');
    bottomNav.className = 'mobile-bottom-nav';
    
    // Define navigation items
    const navItems = [
      { icon: '🏠', label: 'Home', href: '/', id: 'home' },
      { icon: '📚', label: 'Learn', href: '#', id: 'learn' },
      { icon: '🛠️', label: 'Tools', href: '/tools/', id: 'tools' },
      { icon: '📖', label: 'Reference', href: '/reference/', id: 'reference' },
      { icon: '☰', label: 'Menu', href: '#', id: 'menu' }
    ];
    
    // Create navigation items
    navItems.forEach(item => {
      const navLink = document.createElement('a');
      navLink.className = 'mobile-nav-item';
      navLink.href = item.href;
      navLink.id = `mobile-nav-${item.id}`;
      navLink.innerHTML = `
        <span class="mobile-nav-icon">${item.icon}</span>
        <span class="mobile-nav-label">${item.label}</span>
      `;
      
      // Handle special items
      if (item.id === 'menu') {
        navLink.addEventListener('click', (e) => {
          e.preventDefault();
          this.toggleMobileMenu();
        });
      } else if (item.id === 'learn') {
        navLink.addEventListener('click', (e) => {
          e.preventDefault();
          this.showLearnMenu();
        });
      }
      
      // Mark active item
      if (this.isCurrentSection(item.href)) {
        navLink.classList.add('active');
      }
      
      bottomNav.appendChild(navLink);
    });
    
    // Add to body
    document.body.appendChild(bottomNav);
    
    // Adjust content padding
    this.adjustContentForBottomNav();
    
    // Create learn menu
    this.createLearnMenu();
  }
  
  createLearnMenu() {
    const learnMenu = document.createElement('div');
    learnMenu.className = 'mobile-learn-menu';
    learnMenu.innerHTML = `
      <div class="mobile-menu-backdrop"></div>
      <div class="mobile-menu-panel">
        <div class="mobile-menu-header">
          <h3>Learn</h3>
          <button class="mobile-menu-close">×</button>
        </div>
        <div class="mobile-menu-content">
          <a href="/part1-axioms/" class="mobile-menu-item">
            <span class="menu-item-icon">🔷</span>
            <div class="menu-item-content">
              <span class="menu-item-title">Part I: Axioms</span>
              <span class="menu-item-desc">8 fundamental principles</span>
            </div>
          </a>
          <a href="/part2-pillars/" class="mobile-menu-item">
            <span class="menu-item-icon">🏛️</span>
            <div class="menu-item-content">
              <span class="menu-item-title">Part II: Pillars</span>
              <span class="menu-item-desc">6 foundational patterns</span>
            </div>
          </a>
          <a href="/part4-case-study/" class="mobile-menu-item">
            <span class="menu-item-icon">📊</span>
            <div class="menu-item-content">
              <span class="menu-item-title">Case Study</span>
              <span class="menu-item-desc">Real-world application</span>
            </div>
          </a>
          <a href="/part6-advanced/" class="mobile-menu-item">
            <span class="menu-item-icon">🚀</span>
            <div class="menu-item-content">
              <span class="menu-item-title">Advanced Topics</span>
              <span class="menu-item-desc">Cutting-edge concepts</span>
            </div>
          </a>
        </div>
      </div>
    `;
    
    document.body.appendChild(learnMenu);
    
    // Event listeners
    learnMenu.querySelector('.mobile-menu-backdrop').addEventListener('click', () => {
      this.hideLearnMenu();
    });
    
    learnMenu.querySelector('.mobile-menu-close').addEventListener('click', () => {
      this.hideLearnMenu();
    });
  }
  
  setupSwipeGestures() {
    let touchStartTime = 0;
    
    // Touch event handlers
    document.addEventListener('touchstart', (e) => {
      this.touchStartX = e.changedTouches[0].screenX;
      this.touchStartY = e.changedTouches[0].screenY;
      this.touchStartTime = Date.now();
      this.isScrolling = false;
    }, { passive: true });
    
    document.addEventListener('touchmove', (e) => {
      if (!this.touchStartX || !this.touchStartY) return;
      
      const xDiff = Math.abs(e.changedTouches[0].screenX - this.touchStartX);
      const yDiff = Math.abs(e.changedTouches[0].screenY - this.touchStartY);
      
      // Determine if scrolling vertically
      if (yDiff > xDiff) {
        this.isScrolling = true;
      }
    }, { passive: true });
    
    document.addEventListener('touchend', (e) => {
      if (this.isScrolling) return;
      
      this.touchEndX = e.changedTouches[0].screenX;
      this.touchEndY = e.changedTouches[0].screenY;
      
      const touchDuration = Date.now() - this.touchStartTime;
      const velocity = Math.abs(this.touchEndX - this.touchStartX) / touchDuration;
      
      this.handleSwipe(velocity);
      
      // Reset
      this.touchStartX = 0;
      this.touchStartY = 0;
    }, { passive: true });
    
    // Add swipe hints
    this.addSwipeHints();
  }
  
  handleSwipe(velocity) {
    const xDiff = this.touchEndX - this.touchStartX;
    const yDiff = this.touchEndY - this.touchStartY;
    
    // Check if horizontal swipe
    if (Math.abs(xDiff) > Math.abs(yDiff) && Math.abs(xDiff) > this.swipeThreshold) {
      if (velocity > this.velocityThreshold) {
        if (xDiff > 0) {
          // Swipe right - previous page
          this.navigatePrevious();
          this.showSwipeHint('← Previous page');
        } else {
          // Swipe left - next page
          this.navigateNext();
          this.showSwipeHint('Next page →');
        }
      }
    }
  }
  
  navigateNext() {
    const nextLink = document.querySelector('.md-footer__link--next');
    if (nextLink) {
      // Add haptic feedback if available
      this.hapticFeedback();
      nextLink.click();
    }
  }
  
  navigatePrevious() {
    const prevLink = document.querySelector('.md-footer__link--prev');
    if (prevLink) {
      // Add haptic feedback if available
      this.hapticFeedback();
      prevLink.click();
    }
  }
  
  addSwipeHints() {
    const swipeHint = document.createElement('div');
    swipeHint.className = 'swipe-hint';
    swipeHint.textContent = 'Swipe to navigate';
    document.body.appendChild(swipeHint);
    
    // Show hint on first visit
    if (!localStorage.getItem('swipe-hint-shown')) {
      setTimeout(() => {
        this.showSwipeHint('Swipe left/right to navigate');
        localStorage.setItem('swipe-hint-shown', 'true');
      }, 2000);
    }
  }
  
  showSwipeHint(text) {
    const hint = document.querySelector('.swipe-hint');
    if (hint) {
      hint.textContent = text;
      hint.classList.add('show');
      
      setTimeout(() => {
        hint.classList.remove('show');
      }, 2000);
    }
  }
  
  optimizeTouchTargets() {
    // Ensure all interactive elements meet minimum touch target size
    const minSize = 44; // iOS Human Interface Guidelines
    
    const interactiveElements = document.querySelectorAll(
      'a, button, input, select, textarea'
    );
    
    interactiveElements.forEach(element => {
      const rect = element.getBoundingClientRect();
      
      if (rect.width < minSize || rect.height < minSize) {
        element.style.minWidth = `${minSize}px`;
        element.style.minHeight = `${minSize}px`;
        element.style.display = 'inline-flex';
        element.style.alignItems = 'center';
        element.style.justifyContent = 'center';
      }
      
      // Add touch feedback
      element.addEventListener('touchstart', () => {
        element.classList.add('touch-active');
      }, { passive: true });
      
      element.addEventListener('touchend', () => {
        setTimeout(() => {
          element.classList.remove('touch-active');
        }, 100);
      }, { passive: true });
    });
  }
  
  addMobileOptimizations() {
    // Disable pull-to-refresh on Chrome
    document.body.style.overscrollBehavior = 'none';
    
    // Add viewport meta tag adjustments
    let viewport = document.querySelector('meta[name="viewport"]');
    if (!viewport) {
      viewport = document.createElement('meta');
      viewport.name = 'viewport';
      document.head.appendChild(viewport);
    }
    viewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes';
    
    // Optimize images for mobile
    this.optimizeImages();
    
    // Add mobile-specific classes
    document.body.classList.add('is-mobile');
    if ('ontouchstart' in window) {
      document.body.classList.add('touch-device');
    }
  }
  
  optimizeImages() {
    const images = document.querySelectorAll('img');
    
    images.forEach(img => {
      // Add loading lazy attribute
      img.loading = 'lazy';
      
      // Ensure images are responsive
      if (!img.style.maxWidth) {
        img.style.maxWidth = '100%';
        img.style.height = 'auto';
      }
    });
  }
  
  setupOrientationHandler() {
    const handleOrientation = () => {
      const isLandscape = window.innerWidth > window.innerHeight;
      
      if (isLandscape) {
        document.body.classList.add('landscape-mobile');
      } else {
        document.body.classList.remove('landscape-mobile');
      }
      
      // Adjust bottom nav for landscape
      this.adjustContentForBottomNav();
    };
    
    window.addEventListener('orientationchange', handleOrientation);
    window.addEventListener('resize', handleOrientation);
    
    // Initial check
    handleOrientation();
  }
  
  adjustContentForBottomNav() {
    const bottomNavHeight = 56;
    const content = document.querySelector('.md-container');
    
    if (content) {
      content.style.paddingBottom = `${bottomNavHeight + 20}px`;
    }
    
    // Adjust FAB buttons
    const fabButtons = document.querySelectorAll('.help-button, .mobile-toc-toggle');
    fabButtons.forEach(button => {
      const currentBottom = parseInt(window.getComputedStyle(button).bottom) || 20;
      button.style.bottom = `${currentBottom + bottomNavHeight + 10}px`;
    });
  }
  
  toggleMobileMenu() {
    const drawer = document.querySelector('[data-md-toggle="drawer"]');
    if (drawer) {
      drawer.checked = !drawer.checked;
      drawer.dispatchEvent(new Event('change'));
    }
  }
  
  showLearnMenu() {
    const menu = document.querySelector('.mobile-learn-menu');
    if (menu) {
      menu.classList.add('show');
      document.body.style.overflow = 'hidden';
    }
  }
  
  hideLearnMenu() {
    const menu = document.querySelector('.mobile-learn-menu');
    if (menu) {
      menu.classList.remove('show');
      document.body.style.overflow = '';
    }
  }
  
  isCurrentSection(href) {
    const currentPath = window.location.pathname;
    
    if (href === '/') {
      return currentPath === '/' || currentPath === '/index.html';
    }
    
    return currentPath.startsWith(href);
  }
  
  hapticFeedback() {
    // Use Vibration API if available
    if ('vibrate' in navigator) {
      navigator.vibrate(10);
    }
  }
}

// Initialize mobile navigation
document.addEventListener('DOMContentLoaded', () => {
  new MobileNavigation();
});