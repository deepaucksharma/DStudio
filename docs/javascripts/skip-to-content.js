// Skip to Content Link Implementation
document.addEventListener('DOMContentLoaded', () => {
  // Create skip to content link
  const skipLink = document.createElement('a');
  skipLink.href = '#main-content';
  skipLink.className = 'skip-to-content';
  skipLink.textContent = 'Skip to main content';
  
  // Insert at the beginning of body
  document.body.insertBefore(skipLink, document.body.firstChild);
  
  // Add ID to main content area if not present
  const mainContent = document.querySelector('.md-content') || 
                     document.querySelector('.md-main__inner') || 
                     document.querySelector('main');
  
  if (mainContent && !mainContent.id) {
    mainContent.id = 'main-content';
  }
  
  // Handle click to ensure proper focus
  skipLink.addEventListener('click', (e) => {
    e.preventDefault();
    const target = document.querySelector(skipLink.getAttribute('href'));
    if (target) {
      target.setAttribute('tabindex', '-1');
      target.focus();
      window.scrollTo({
        top: target.offsetTop,
        behavior: 'smooth'
      });
    }
  });
});

// Persist sidebar scroll position
(() => {
  const STORAGE_KEY = 'sidebar-scroll-positions';
  
  // Save scroll positions
  const saveScrollPositions = () => {
    const positions = {};
    const sidebars = document.querySelectorAll('.md-sidebar__scrollwrap');
    
    sidebars.forEach((sidebar, index) => {
      positions[`sidebar-${index}`] = sidebar.scrollTop;
    });
    
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(positions));
  };
  
  // Restore scroll positions
  const restoreScrollPositions = () => {
    const saved = sessionStorage.getItem(STORAGE_KEY);
    if (!saved) return;
    
    try {
      const positions = JSON.parse(saved);
      const sidebars = document.querySelectorAll('.md-sidebar__scrollwrap');
      
      sidebars.forEach((sidebar, index) => {
        const position = positions[`sidebar-${index}`];
        if (position !== undefined) {
          sidebar.scrollTop = position;
        }
      });
    } catch (e) {
      console.error('Error restoring sidebar positions:', e);
    }
  };
  
  // Set up event listeners
  document.addEventListener('DOMContentLoaded', () => {
    // Restore on load
    setTimeout(restoreScrollPositions, 100);
    
    // Save on scroll
    const sidebars = document.querySelectorAll('.md-sidebar__scrollwrap');
    sidebars.forEach(sidebar => {
      let scrollTimeout;
      sidebar.addEventListener('scroll', () => {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(saveScrollPositions, 100);
      });
    });
    
    // Save before navigation
    window.addEventListener('beforeunload', saveScrollPositions);
  });
})();

// Progress indicators for multi-part content
class PartProgressIndicator {
  constructor() {
    this.currentPath = window.location.pathname;
    this.init();
  }
  
  init() {
    // Define part structures
    const parts = {
      'part1-axioms': {
        name: 'Part I: Axioms',
        sections: [
          'axiom-1-latency',
          'axiom-2-capacity',
          'axiom-3-failure',
          'axiom-4-concurrency',
          'axiom-5-coordination',
          'axiom-6-observability',
          'axiom-7-human-interface',
          'axiom-8-economics'
        ]
      },
      'part2-pillars': {
        name: 'Part II: Pillars',
        sections: [
          'pillar-1-work',
          'pillar-2-state',
          'pillar-3-truth',
          'pillar-4-control',
          'pillar-5-intelligence',
          'pillar-6-trust'
        ]
      }
    };
    
    // Check if we're in a multi-part section
    for (const [partKey, partData] of Object.entries(parts)) {
      if (this.currentPath.includes(partKey)) {
        this.createProgressIndicator(partData, partKey);
        break;
      }
    }
  }
  
  createProgressIndicator(partData, partKey) {
    // Find current section
    let currentIndex = -1;
    partData.sections.forEach((section, index) => {
      if (this.currentPath.includes(section)) {
        currentIndex = index;
      }
    });
    
    if (currentIndex === -1) return;
    
    const progress = ((currentIndex + 1) / partData.sections.length) * 100;
    
    // Create progress element
    const progressElement = document.createElement('div');
    progressElement.className = 'part-progress';
    progressElement.innerHTML = `
      <span class="part-progress-label">${partData.name}</span>
      <div class="part-progress-bar">
        <div class="part-progress-fill" style="width: ${progress}%"></div>
      </div>
      <span class="part-progress-text">${currentIndex + 1} of ${partData.sections.length}</span>
    `;
    
    // Insert after header
    const header = document.querySelector('.md-content h1');
    if (header && header.parentNode) {
      header.parentNode.insertBefore(progressElement, header.nextSibling);
    }
  }
}

// Initialize progress indicator
document.addEventListener('DOMContentLoaded', () => {
  new PartProgressIndicator();
});