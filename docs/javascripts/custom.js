/* Minimal Custom JavaScript for The Compendium of Distributed Systems */

(function() {
  'use strict';

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

  // === Mermaid Initialization ===
  
  function initializeMermaid() {
    if (typeof mermaid !== 'undefined') {
      mermaid.initialize({
        startOnLoad: true,
        theme: 'default',
        themeVariables: {
          primaryColor: '#5448C8',
          primaryTextColor: '#ffffff',
          primaryBorderColor: '#5448C8',
          lineColor: '#6366f1',
          sectionBkgColor: '#f8fafc',
          altSectionBkgColor: '#f1f5f9',
          gridColor: '#e2e8f0',
          secondaryColor: '#00BCD4',
          tertiaryColor: '#f3f4f6'
        }
      });
      // Render any mermaid diagrams
      mermaid.contentLoaded();
    }
  }

  // === Initialize Everything ===
  
  function initialize() {
    enhanceSearch();
    enhanceExternalLinks();
    
    // Initialize mermaid if available
    if (typeof mermaid !== 'undefined') {
      initializeMermaid();
    } else {
      // Try again after a short delay
      setTimeout(function() {
        if (typeof mermaid !== 'undefined') {
          initializeMermaid();
        }
      }, 1000);
    }
  }

  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }

})();