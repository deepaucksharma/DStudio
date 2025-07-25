/* UI Enhancements for DStudio */

document.addEventListener('DOMContentLoaded', function() {
  
  // Add skip to content link
  const skipLink = document.createElement('a');
  skipLink.href = '#main-content';
  skipLink.className = 'skip-nav';
  skipLink.textContent = 'Skip to main content';
  document.body.insertBefore(skipLink, document.body.firstChild);
  
  // Add main content ID if not present
  const mainContent = document.querySelector('.md-content');
  if (mainContent && !mainContent.id) {
    mainContent.id = 'main-content';
  }
  
  // Enhance table responsiveness
  const tables = document.querySelectorAll('.md-typeset table');
  tables.forEach(table => {
    if (!table.classList.contains('responsive-table')) {
      // Wrap table in scrollable container
      const wrapper = document.createElement('div');
      wrapper.className = 'table-wrapper';
      table.parentNode.insertBefore(wrapper, table);
      wrapper.appendChild(table);
    }
  });
  
  // Remove emojis from navigation dynamically
  const navEmojis = document.querySelectorAll('.md-nav__link .twemoji, .md-tabs__link .twemoji');
  navEmojis.forEach(emoji => emoji.remove());
  
  // Add smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
  
  // Improve mobile navigation toggle
  const navToggle = document.querySelector('[data-md-toggle="drawer"]');
  if (navToggle) {
    navToggle.addEventListener('click', function() {
      document.body.classList.toggle('md-nav-open');
    });
  }
  
  // Add aria-labels to icon-only buttons
  document.querySelectorAll('.md-header__button').forEach(button => {
    if (!button.getAttribute('aria-label')) {
      const icon = button.querySelector('svg');
      if (icon) {
        const title = icon.querySelector('title');
        if (title) {
          button.setAttribute('aria-label', title.textContent);
        }
      }
    }
  });
  
  // Lazy load images
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.classList.remove('lazy');
          observer.unobserve(img);
        }
      });
    });
    
    document.querySelectorAll('img[data-src]').forEach(img => {
      imageObserver.observe(img);
    });
  }
  
});

// Add CSS classes based on scroll position
let lastScrollTop = 0;
window.addEventListener('scroll', function() {
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  
  if (scrollTop > lastScrollTop && scrollTop > 100) {
    // Scrolling down
    document.body.classList.add('md-header--hidden');
  } else {
    // Scrolling up
    document.body.classList.remove('md-header--hidden');
  }
  
  lastScrollTop = scrollTop;
}, { passive: true });