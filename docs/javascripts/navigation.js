/* Navigation Enhancement JavaScript */

(function() {
  'use strict';

  // === Page Navigation Helper ===
  
  class PageNavigator {
    constructor() {
      this.initPageNavHelper();
      this.initScrollSpy();
      this.initKeyboardShortcuts();
      this.trackProgress();
    }

    initPageNavHelper() {
      // Create simple quick actions bar
      const navHelper = document.createElement('div');
      navHelper.className = 'page-nav-helper';
      navHelper.innerHTML = `
        <div class="nav-actions">
          <button class="nav-btn" data-action="top" title="Back to top">↑ Top</button>
          <button class="nav-btn" data-action="share" title="Share page">📤 Share</button>
        </div>
      `;

      document.body.appendChild(navHelper);

      // Handle nav actions
      navHelper.addEventListener('click', (e) => {
        if (e.target.matches('.nav-btn')) {
          const action = e.target.dataset.action;
          this.handleNavAction(action);
        }
      });

      // Smooth scroll for nav items
      quickNav.addEventListener('click', (e) => {
        if (e.target.matches('.nav-item')) {
          e.preventDefault();
          const target = document.querySelector(e.target.getAttribute('href'));
          if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }
      });
    }

    handleNavAction(action) {
      switch(action) {
        case 'top':
          window.scrollTo({ top: 0, behavior: 'smooth' });
          break;
        case 'print':
          window.print();
          break;
        case 'share':
          this.shareCurrentPage();
          break;
      }
    }

    shareCurrentPage() {
      const url = window.location.href;
      const title = document.title;
      
      if (navigator.share) {
        navigator.share({ title, url })
          .catch(err => console.log('Share failed:', err));
      } else {
        // Fallback: Copy to clipboard
        navigator.clipboard.writeText(url).then(() => {
          this.showToast('Link copied to clipboard!');
        });
      }
    }

    showToast(message) {
      const toast = document.createElement('div');
      toast.className = 'nav-toast';
      toast.textContent = message;
      toast.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        background: var(--md-primary-fg-color);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 1000;
        animation: slideIn 0.3s ease;
      `;
      
      document.body.appendChild(toast);
      
      setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
      }, 3000);
    }

    initScrollSpy() {
      const navItems = document.querySelectorAll('.page-nav-helper .nav-item');
      if (!navItems.length) return;

      const observerOptions = {
        rootMargin: '-20% 0px -70% 0px',
        threshold: 0
      };

      const observerCallback = (entries) => {
        entries.forEach(entry => {
          const id = entry.target.getAttribute('id');
          const navItem = document.querySelector(`.nav-item[href="#${id}"]`);
          
          if (navItem) {
            if (entry.isIntersecting) {
              navItems.forEach(item => item.classList.remove('active'));
              navItem.classList.add('active');
            }
          }
        });
      };

      const observer = new IntersectionObserver(observerCallback, observerOptions);
      
      document.querySelectorAll('h2[id], h3[id]').forEach(heading => {
        observer.observe(heading);
      });
    }

    initKeyboardShortcuts() {
      document.addEventListener('keydown', (e) => {
        // Alt + N: Next page
        if (e.altKey && e.key === 'n') {
          e.preventDefault();
          const nextLink = document.querySelector('.md-footer__link--next');
          if (nextLink) nextLink.click();
        }
        
        // Alt + P: Previous page
        if (e.altKey && e.key === 'p') {
          e.preventDefault();
          const prevLink = document.querySelector('.md-footer__link--prev');
          if (prevLink) prevLink.click();
        }
        
        // Alt + U: Up one level
        if (e.altKey && e.key === 'u') {
          e.preventDefault();
          const pathSegments = window.location.pathname.split('/').filter(s => s);
          if (pathSegments.length > 1) {
            pathSegments.pop();
            window.location.href = '/' + pathSegments.join('/') + '/';
          }
        }
        
        // ? : Show shortcuts
        if (e.key === '?' && !e.ctrlKey && !e.metaKey) {
          e.preventDefault();
          this.showShortcutsHelp();
        }
      });
    }

    showShortcutsHelp() {
      const modal = document.createElement('div');
      modal.className = 'shortcuts-modal';
      modal.innerHTML = `
        <div class="shortcuts-content">
          <h3>Keyboard Shortcuts</h3>
          <button class="close-btn" onclick="this.closest('.shortcuts-modal').remove()">×</button>
          <dl>
            <dt><kbd>Ctrl</kbd> + <kbd>K</kbd></dt>
            <dd>Search documentation</dd>
            
            <dt><kbd>Alt</kbd> + <kbd>N</kbd></dt>
            <dd>Next page</dd>
            
            <dt><kbd>Alt</kbd> + <kbd>P</kbd></dt>
            <dd>Previous page</dd>
            
            <dt><kbd>Alt</kbd> + <kbd>U</kbd></dt>
            <dd>Up one level</dd>
            
            <dt><kbd>Alt</kbd> + <kbd>←</kbd></dt>
            <dd>Navigate back</dd>
            
            <dt><kbd>Alt</kbd> + <kbd>→</kbd></dt>
            <dd>Navigate forward</dd>
            
            <dt><kbd>?</kbd></dt>
            <dd>Show this help</dd>
          </dl>
        </div>
      `;
      
      modal.style.cssText = `
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 2000;
      `;
      
      const content = modal.querySelector('.shortcuts-content');
      content.style.cssText = `
        background: var(--md-default-bg-color);
        padding: 2rem;
        border-radius: 0.5rem;
        max-width: 500px;
        width: 90%;
        max-height: 80vh;
        overflow-y: auto;
        position: relative;
      `;
      
      document.body.appendChild(modal);
      
      // Close on click outside
      modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
      });
      
      // Close on Escape
      const escHandler = (e) => {
        if (e.key === 'Escape') {
          modal.remove();
          document.removeEventListener('keydown', escHandler);
        }
      };
      document.addEventListener('keydown', escHandler);
    }

    trackProgress() {
      const sequence = document.querySelector('[data-sequence-current]');
      if (!sequence) return;
      
      const current = parseInt(sequence.dataset.sequenceCurrent);
      const total = parseInt(sequence.dataset.sequenceTotal);
      
      if (current && total) {
        // Save progress to localStorage
        const progress = JSON.parse(localStorage.getItem('learningProgress') || '{}');
        const path = window.location.pathname;
        
        progress[path] = {
          completed: true,
          timestamp: Date.now(),
          sequence: { current, total }
        };
        
        localStorage.setItem('learningProgress', JSON.stringify(progress));
        
        // Update progress indicators
        this.updateProgressIndicators(progress);
      }
    }

    updateProgressIndicators(progress) {
      // Count completed pages
      const completed = Object.keys(progress).length;
      
      // Update any progress displays
      document.querySelectorAll('[data-progress-count]').forEach(el => {
        el.textContent = completed;
      });
    }
  }

  // === Learning Path Tracker ===
  
  class LearningPathTracker {
    constructor() {
      this.initTracker();
    }

    initTracker() {
      const pathBadge = document.querySelector('.learning-path-badge');
      if (!pathBadge) return;
      
      const pathName = pathBadge.dataset.path;
      if (!pathName) return;
      
      // Track time spent
      const startTime = Date.now();
      
      window.addEventListener('beforeunload', () => {
        const timeSpent = Date.now() - startTime;
        this.trackPageVisit(pathName, timeSpent);
      });
      
      // Show progress summary
      this.showProgressSummary(pathName);
    }

    trackPageVisit(pathName, timeSpent) {
      const stats = JSON.parse(localStorage.getItem('pathStats') || '{}');
      
      if (!stats[pathName]) {
        stats[pathName] = {
          visits: 0,
          totalTime: 0,
          lastVisit: null
        };
      }
      
      stats[pathName].visits++;
      stats[pathName].totalTime += timeSpent;
      stats[pathName].lastVisit = Date.now();
      
      localStorage.setItem('pathStats', JSON.stringify(stats));
    }

    showProgressSummary(pathName) {
      const stats = JSON.parse(localStorage.getItem('pathStats') || '{}');
      const pathStats = stats[pathName];
      
      if (pathStats && pathStats.visits > 1) {
        const summary = document.createElement('div');
        summary.className = 'progress-summary';
        summary.innerHTML = `
          <div class="summary-content">
            <span>Welcome back! You've visited ${pathStats.visits} times.</span>
            <span>Total time: ${this.formatTime(pathStats.totalTime)}</span>
          </div>
        `;
        
        const firstHeading = document.querySelector('h1');
        if (firstHeading) {
          firstHeading.parentNode.insertBefore(summary, firstHeading.nextSibling);
        }
      }
    }

    formatTime(ms) {
      const minutes = Math.floor(ms / 60000);
      if (minutes < 60) return `${minutes} min`;
      const hours = Math.floor(minutes / 60);
      return `${hours}h ${minutes % 60}m`;
    }
  }

  // === Smart Related Content ===
  
  class SmartRelatedContent {
    constructor() {
      this.enhanceRelatedLinks();
    }

    enhanceRelatedLinks() {
      const relatedSection = document.querySelector('.related-content');
      if (!relatedSection) return;
      
      // Add view tracking
      const links = relatedSection.querySelectorAll('a');
      links.forEach(link => {
        link.addEventListener('click', () => {
          this.trackRelatedClick(link.href);
        });
      });
      
      // Reorder based on popularity
      this.reorderByPopularity(relatedSection);
    }

    trackRelatedClick(href) {
      const clicks = JSON.parse(localStorage.getItem('relatedClicks') || '{}');
      clicks[href] = (clicks[href] || 0) + 1;
      localStorage.setItem('relatedClicks', JSON.stringify(clicks));
    }

    reorderByPopularity(section) {
      const clicks = JSON.parse(localStorage.getItem('relatedClicks') || '{}');
      const items = Array.from(section.querySelectorAll('.related-item'));
      
      items.sort((a, b) => {
        const aClicks = clicks[a.href] || 0;
        const bClicks = clicks[b.href] || 0;
        return bClicks - aClicks;
      });
      
      const grid = section.querySelector('.related-grid');
      if (grid) {
        items.forEach(item => grid.appendChild(item));
      }
    }
  }

  // === Initialize Everything ===
  
  function initialize() {
    // Add CSS for animations
    const style = document.createElement('style');
    style.textContent = `
      @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
      }
      
      @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
      }
      
      .shortcuts-modal kbd {
        background: var(--md-code-bg-color);
        padding: 0.2rem 0.4rem;
        border-radius: 0.2rem;
        font-family: var(--md-code-font-family);
        font-size: 0.85em;
      }
      
      .shortcuts-modal dt {
        margin-bottom: 0.5rem;
      }
      
      .shortcuts-modal dd {
        margin-left: 0;
        margin-bottom: 1rem;
        color: var(--md-default-fg-color--light);
      }
      
      .progress-summary {
        background: var(--md-primary-fg-color--light);
        color: var(--md-primary-fg-color);
        padding: 0.75rem 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        font-size: 0.875rem;
      }
      
      .close-btn {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: var(--md-default-fg-color);
      }
    `;
    document.head.appendChild(style);
    
    // Initialize components
    new PageNavigator();
    new LearningPathTracker();
    new SmartRelatedContent();
  }

  // Wait for DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }

})();