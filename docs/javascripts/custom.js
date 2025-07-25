/* Custom JavaScript for The Compendium of Distributed Systems */
/* Performance-optimized and following best practices */

(function() {
  'use strict';

  // === Performance Monitoring ===
  
  // Log performance metrics
  window.addEventListener('load', function() {
    if ('performance' in window) {
      const perfData = window.performance.timing;
      const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
      const connectTime = perfData.responseEnd - perfData.requestStart;
      const renderTime = perfData.domComplete - perfData.domLoading;
      
      console.log('Performance Metrics:', {
        'Page Load Time': pageLoadTime + 'ms',
        'Connect Time': connectTime + 'ms',
        'Render Time': renderTime + 'ms'
      });
    }
  });

  // === Reading Progress Indicator ===
  
  function createProgressBar() {
    const progress = document.createElement('div');
    progress.className = 'reading-progress';
    document.body.appendChild(progress);
    
    function updateProgress() {
      const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = (winScroll / height);
      progress.style.transform = `scaleX(${scrolled})`;
    }
    
    // Throttle scroll events for performance
    let ticking = false;
    function requestTick() {
      if (!ticking) {
        window.requestAnimationFrame(updateProgress);
        ticking = true;
        setTimeout(() => ticking = false, 100);
      }
    }
    
    window.addEventListener('scroll', requestTick);
  }

  // === Enhanced Search Experience ===
  
  function enhanceSearch() {
    const searchInput = document.querySelector('.md-search__input');
    if (!searchInput) return;
    
    // Add search shortcuts
    document.addEventListener('keydown', function(e) {
      // Cmd/Ctrl + K to focus search
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        searchInput.focus();
      }
      // Escape to close search
      if (e.key === 'Escape' && document.activeElement === searchInput) {
        searchInput.blur();
      }
    });
  }

  // === Copy Code Enhancement ===
  
  function enhanceCodeBlocks() {
    // Add filename display to code blocks with title
    document.querySelectorAll('pre > code').forEach(block => {
      const pre = block.parentElement;
      const title = pre.getAttribute('title');
      
      if (title) {
        const filename = document.createElement('span');
        filename.className = 'filename';
        filename.textContent = title;
        pre.appendChild(filename);
      }
    });
    
    // Enhance copy button feedback
    document.addEventListener('click', function(e) {
      if (e.target.matches('.md-clipboard')) {
        const button = e.target;
        const originalTitle = button.getAttribute('title');
        
        button.setAttribute('title', 'Copied!');
        button.classList.add('copied');
        
        setTimeout(() => {
          button.setAttribute('title', originalTitle);
          button.classList.remove('copied');
        }, 2000);
      }
    });
  }

  // === Table of Contents Enhancement - REMOVED ===
  // TOC functionality has been removed as per requirements

  // === Fix Navigation for Instant Loading ===
  
  function fixInstantNavigation() {
    // Listen for navigation changes
    if (window.location$ && window.location$.subscribe) {
      window.location$.subscribe(() => {
        // Small delay to ensure DOM is updated
        setTimeout(() => {
          // Update active navigation items in left sidebar
          const activeNavItem = document.querySelector('.md-nav__item--active');
          if (activeNavItem) {
            activeNavItem.scrollIntoView({ block: 'center' });
          }
        }, 100);
      });
    }
  }

  // === Lazy Loading for Images ===
  
  function setupLazyLoading() {
    if ('IntersectionObserver' in window) {
      const images = document.querySelectorAll('img[loading="lazy"]');
      const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src || img.src;
            img.classList.add('loaded');
            observer.unobserve(img);
          }
        });
      });
      
      images.forEach(img => imageObserver.observe(img));
    }
  }

  // === External Link Enhancement ===
  
  function enhanceExternalLinks() {
    document.querySelectorAll('a[href^="http"]').forEach(link => {
      if (!link.href.includes(window.location.hostname)) {
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');
        link.classList.add('external-link');
      }
    });
  }

  // === Keyboard Navigation ===
  
  function setupKeyboardNav() {
    document.addEventListener('keydown', function(e) {
      // Navigate between pages with arrow keys
      if (e.altKey) {
        if (e.key === 'ArrowLeft') {
          const prevLink = document.querySelector('.md-footer__link--prev');
          if (prevLink) prevLink.click();
        } else if (e.key === 'ArrowRight') {
          const nextLink = document.querySelector('.md-footer__link--next');
          if (nextLink) nextLink.click();
        }
      }
    });
  }

  // === Initialize Everything ===
  
  function initialize() {
    createProgressBar();
    enhanceSearch();
    enhanceCodeBlocks();
    // TOC functions removed - using left navigation only
    fixInstantNavigation();
    setupLazyLoading();
    enhanceExternalLinks();
    setupKeyboardNav();
    
    // Add loaded class for CSS animations
    document.body.classList.add('loaded');
  }

  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }

  // === Service Worker for Offline Support ===
  
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js').catch(() => {
        // Service worker registration failed, which is fine
      });
    });
  }

})();