/* Mobile Enhancement JavaScript
   Handles dynamic mobile behaviors and scroll indicators
*/

document.addEventListener('DOMContentLoaded', function() {
  // Add horizontal scroll indicators to tables
  function addScrollIndicators() {
    const scrollWraps = document.querySelectorAll('.md-typeset__scrollwrap');
    
    scrollWraps.forEach(wrap => {
      const updateScrollIndicator = () => {
        const maxScroll = wrap.scrollWidth - wrap.clientWidth;
        const currentScroll = wrap.scrollLeft;
        
        if (currentScroll >= maxScroll - 5) {
          wrap.classList.add('scrolled-right');
        } else {
          wrap.classList.remove('scrolled-right');
        }
        
        if (currentScroll > 5) {
          wrap.classList.add('scrolled-left');
        } else {
          wrap.classList.remove('scrolled-left');
        }
      };
      
      wrap.addEventListener('scroll', updateScrollIndicator);
      updateScrollIndicator();
    });
  }
  
  // Wrap tables in scrollable containers on mobile
  function wrapTables() {
    if (window.innerWidth <= 768) {
      const tables = document.querySelectorAll('.md-typeset table:not(.responsive-table):not(.wrapped)');
      
      tables.forEach(table => {
        if (!table.closest('.md-typeset__scrollwrap')) {
          const wrapper = document.createElement('div');
          wrapper.className = 'md-typeset__scrollwrap';
          table.parentNode.insertBefore(wrapper, table);
          wrapper.appendChild(table);
          table.classList.add('wrapped');
        }
      });
      
      addScrollIndicators();
    }
  }
  
  // Handle touch-friendly navigation
  function enhanceTouchTargets() {
    if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
      document.body.classList.add('touch-device');
    }
  }
  
  // Optimize code block scrolling
  function enhanceCodeBlocks() {
    const codeBlocks = document.querySelectorAll('.md-typeset pre');
    
    codeBlocks.forEach(block => {
      // Add visual hint for scrollable code blocks
      const updateScrollHint = () => {
        const maxScroll = block.scrollWidth - block.clientWidth;
        if (maxScroll > 0) {
          block.classList.add('scrollable');
        } else {
          block.classList.remove('scrollable');
        }
      };
      
      updateScrollHint();
      window.addEventListener('resize', updateScrollHint);
    });
  }
  
  // Improve mobile navigation drawer
  function enhanceNavDrawer() {
    const drawer = document.querySelector('.md-sidebar--primary');
    const toggle = document.querySelector('.md-header__button--menu');
    
    if (drawer && toggle) {
      // Close drawer when clicking outside on mobile
      document.addEventListener('click', (e) => {
        if (window.innerWidth <= 1220) {
          const isDrawerOpen = toggle.checked || document.body.classList.contains('drawer-open');
          const clickedInDrawer = drawer.contains(e.target);
          const clickedToggle = toggle.contains(e.target);
          
          if (isDrawerOpen && !clickedInDrawer && !clickedToggle) {
            toggle.checked = false;
            document.body.classList.remove('drawer-open');
          }
        }
      });
    }
  }
  
  // Optimize images for mobile
  function optimizeImages() {
    if ('loading' in HTMLImageElement.prototype) {
      const images = document.querySelectorAll('img:not([loading])');
      images.forEach(img => {
        img.loading = 'lazy';
      });
    }
  }
  
  // Handle orientation changes
  function handleOrientationChange() {
    const updateOrientation = () => {
      if (window.orientation === 90 || window.orientation === -90) {
        document.body.classList.add('landscape');
      } else {
        document.body.classList.remove('landscape');
      }
    };
    
    window.addEventListener('orientationchange', updateOrientation);
    updateOrientation();
  }
  
  // Improve mobile search experience
  function enhanceSearch() {
    const searchInput = document.querySelector('.md-search__input');
    
    if (searchInput) {
      // Prevent zoom on focus for iOS
      searchInput.addEventListener('focus', () => {
        if (window.innerWidth <= 768) {
          document.querySelector('meta[name="viewport"]').content = 
            'width=device-width, initial-scale=1, maximum-scale=1';
        }
      });
      
      searchInput.addEventListener('blur', () => {
        document.querySelector('meta[name="viewport"]').content = 
          'width=device-width, initial-scale=1';
      });
    }
  }
  
  // Add mobile-specific classes based on viewport
  function updateMobileClasses() {
    const width = window.innerWidth;
    const body = document.body;
    
    body.classList.remove('mobile', 'tablet', 'desktop');
    
    if (width < 480) {
      body.classList.add('mobile');
    } else if (width >= 480 && width <= 768) {
      body.classList.add('tablet');
    } else {
      body.classList.add('desktop');
    }
  }
  
  // Initialize all enhancements
  function init() {
    wrapTables();
    enhanceTouchTargets();
    enhanceCodeBlocks();
    enhanceNavDrawer();
    optimizeImages();
    handleOrientationChange();
    enhanceSearch();
    updateMobileClasses();
  }
  
  // Run on load
  init();
  
  // Re-run certain functions on resize
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      wrapTables();
      updateMobileClasses();
    }, 250);
  });
  
  // Handle dynamic content
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.addedNodes.length) {
        wrapTables();
        enhanceCodeBlocks();
        optimizeImages();
      }
    });
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
});