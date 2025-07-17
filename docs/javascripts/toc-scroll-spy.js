// Enhanced Table of Contents with Scroll Spy
class TOCScrollSpy {
  constructor() {
    this.toc = null;
    this.headings = [];
    this.tocLinks = [];
    this.activeLink = null;
    this.scrollTimeout = null;
    this.init();
  }
  
  init() {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.setup());
    } else {
      this.setup();
    }
  }
  
  setup() {
    // Find the table of contents
    this.toc = document.querySelector('.md-sidebar--secondary .md-sidebar__scrollwrap');
    if (!this.toc) return;
    
    // Enhance TOC
    this.enhanceTOC();
    
    // Collect headings and links
    this.collectHeadings();
    
    // Set up scroll spy
    this.setupScrollSpy();
    
    // Add smooth scrolling
    this.addSmoothScrolling();
    
    // Add TOC toggle for mobile
    this.addMobileTOCToggle();
  }
  
  enhanceTOC() {
    // Add enhanced class
    this.toc.classList.add('toc-enhanced');
    
    // Add reading progress to TOC
    const tocProgress = document.createElement('div');
    tocProgress.className = 'toc-progress';
    tocProgress.innerHTML = `
      <div class="toc-progress-bar">
        <div class="toc-progress-fill"></div>
      </div>
      <div class="toc-stats">
        <span class="toc-current-section">Introduction</span>
        <span class="toc-sections-count">1 of 5</span>
      </div>
    `;
    
    const tocNav = this.toc.querySelector('.md-nav');
    if (tocNav && tocNav.firstChild) {
      tocNav.insertBefore(tocProgress, tocNav.firstChild);
    }
    
    this.tocProgressBar = tocProgress.querySelector('.toc-progress-fill');
    this.tocCurrentSection = tocProgress.querySelector('.toc-current-section');
    this.tocSectionsCount = tocProgress.querySelector('.toc-sections-count');
  }
  
  collectHeadings() {
    // Get all headings in the content
    const content = document.querySelector('.md-content');
    if (!content) return;
    
    this.headings = Array.from(content.querySelectorAll('h2, h3, h4'))
      .filter(heading => heading.id)
      .map(heading => ({
        element: heading,
        id: heading.id,
        text: heading.textContent,
        level: parseInt(heading.tagName.charAt(1)),
        top: 0
      }));
    
    // Get corresponding TOC links
    this.tocLinks = Array.from(this.toc.querySelectorAll('a[href^="#"]'))
      .map(link => ({
        element: link,
        href: link.getAttribute('href'),
        parent: link.parentElement
      }));
    
    // Update positions
    this.updateHeadingPositions();
  }
  
  updateHeadingPositions() {
    this.headings.forEach(heading => {
      const rect = heading.element.getBoundingClientRect();
      heading.top = rect.top + window.scrollY - 100; // Offset for fixed header
    });
  }
  
  setupScrollSpy() {
    let ticking = false;
    
    const updateActiveSection = () => {
      const scrollTop = window.scrollY;
      
      // Find current section
      let currentSection = null;
      let currentIndex = 0;
      
      for (let i = this.headings.length - 1; i >= 0; i--) {
        if (scrollTop >= this.headings[i].top - 50) {
          currentSection = this.headings[i];
          currentIndex = i;
          break;
        }
      }
      
      // Update active link
      if (currentSection) {
        this.setActiveLink(currentSection.id);
        
        // Update progress
        const progress = ((currentIndex + 1) / this.headings.length) * 100;
        this.tocProgressBar.style.width = `${progress}%`;
        
        // Update stats
        this.tocCurrentSection.textContent = currentSection.text;
        this.tocSectionsCount.textContent = `${currentIndex + 1} of ${this.headings.length}`;
      }
      
      ticking = false;
    };
    
    // Throttled scroll handler
    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(updateActiveSection);
        ticking = true;
      }
      
      // Update positions periodically
      clearTimeout(this.scrollTimeout);
      this.scrollTimeout = setTimeout(() => {
        this.updateHeadingPositions();
      }, 1000);
    });
    
    // Initial update
    updateActiveSection();
    
    // Update on resize
    window.addEventListener('resize', () => {
      this.updateHeadingPositions();
      updateActiveSection();
    });
  }
  
  setActiveLink(headingId) {
    const targetHref = `#${headingId}`;
    
    // Remove previous active states
    this.tocLinks.forEach(link => {
      link.element.classList.remove('active');
      link.parent.classList.remove('active');
    });
    
    // Find and activate current link
    const activeLink = this.tocLinks.find(link => link.href === targetHref);
    if (activeLink) {
      activeLink.element.classList.add('active');
      activeLink.parent.classList.add('active');
      
      // Ensure active link is visible in TOC
      this.scrollTOCToActive(activeLink.element);
      
      // Expand parent sections if collapsed
      this.expandParentSections(activeLink.element);
    }
  }
  
  scrollTOCToActive(activeElement) {
    const tocContainer = this.toc.querySelector('.md-sidebar__scrollwrap');
    if (!tocContainer) return;
    
    const containerRect = tocContainer.getBoundingClientRect();
    const elementRect = activeElement.getBoundingClientRect();
    
    // Check if element is outside viewport
    if (elementRect.top < containerRect.top || elementRect.bottom > containerRect.bottom) {
      // Scroll element into center of TOC
      const scrollTop = activeElement.offsetTop - tocContainer.offsetTop - (containerRect.height / 2) + (elementRect.height / 2);
      tocContainer.scrollTo({
        top: scrollTop,
        behavior: 'smooth'
      });
    }
  }
  
  expandParentSections(element) {
    let parent = element.parentElement;
    while (parent && parent !== this.toc) {
      if (parent.classList.contains('md-nav__item--nested')) {
        const toggle = parent.querySelector('.md-nav__toggle');
        if (toggle && !toggle.checked) {
          toggle.checked = true;
        }
      }
      parent = parent.parentElement;
    }
  }
  
  addSmoothScrolling() {
    this.tocLinks.forEach(link => {
      link.element.addEventListener('click', (e) => {
        e.preventDefault();
        const targetId = link.href.substring(1);
        const targetElement = document.getElementById(targetId);
        
        if (targetElement) {
          const offset = 80; // Account for fixed header
          const targetPosition = targetElement.offsetTop - offset;
          
          window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
          });
          
          // Update URL without jumping
          history.pushState(null, null, link.href);
        }
      });
    });
  }
  
  addMobileTOCToggle() {
    // Create mobile TOC button
    const tocToggle = document.createElement('button');
    tocToggle.className = 'mobile-toc-toggle';
    tocToggle.innerHTML = `
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path d="M3 12h18M3 6h18M3 18h18" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <span>Contents</span>
    `;
    tocToggle.setAttribute('aria-label', 'Toggle table of contents');
    
    // Add to page
    document.body.appendChild(tocToggle);
    
    // Create mobile TOC overlay
    const mobileOverlay = document.createElement('div');
    mobileOverlay.className = 'mobile-toc-overlay';
    mobileOverlay.addEventListener('click', () => this.closeMobileTOC());
    document.body.appendChild(mobileOverlay);
    
    // Toggle functionality
    tocToggle.addEventListener('click', () => this.toggleMobileTOC());
    
    // Close on link click
    this.tocLinks.forEach(link => {
      link.element.addEventListener('click', () => this.closeMobileTOC());
    });
  }
  
  toggleMobileTOC() {
    document.body.classList.toggle('mobile-toc-open');
    const isOpen = document.body.classList.contains('mobile-toc-open');
    
    if (isOpen) {
      // Focus first link for accessibility
      setTimeout(() => {
        const firstLink = this.toc.querySelector('a');
        if (firstLink) firstLink.focus();
      }, 300);
    }
  }
  
  closeMobileTOC() {
    document.body.classList.remove('mobile-toc-open');
  }
}

// Initialize TOC scroll spy
const tocScrollSpy = new TOCScrollSpy();