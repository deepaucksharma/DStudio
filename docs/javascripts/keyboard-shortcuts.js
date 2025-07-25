/* Advanced Keyboard Shortcuts for MkDocs Material */
(function() {
  'use strict';

  // Keyboard shortcut mappings
  const shortcuts = {
    // Navigation
    'cmd+k,ctrl+k': () => focusSearch(),
    'escape': () => handleEscape(),
    'alt+left': () => navigatePrev(),
    'alt+right': () => navigateNext(),
    'alt+up': () => navigateUp(),
    'g h': () => goHome(),
    'g s': () => focusSearch(),
    'g t': () => goToTags(),
    'g g': () => goToGlossary(),
    
    // Scrolling
    'j': () => smoothScroll(100),
    'k': () => smoothScroll(-100),
    'h': () => jumpToPrevHeading(),
    'l': () => jumpToNextHeading(),
    'home': () => scrollToTop(),
    'end': () => scrollToBottom(),
    
    // Theme & Display
    't': () => toggleTheme(),
    'f': () => toggleFullscreen(),
    'shift+s': () => toggleSidebar(),
    'shift+t': () => toggleTOC(),
    
    // Content Actions
    'e': () => editPage(),
    'v': () => viewSource(),
    'i': () => showPageInfo(),
    '?': () => showHelp(),
    's': () => sharePage(),
    
    // Interactive
    'space': () => toggleDetails(),
    '/': () => focusSearch(),
    ',': () => openSettings(),
    '.': () => openCommandPalette()
  };

  // Key sequence tracking for multi-key shortcuts
  let keySequence = [];
  let sequenceTimer;

  // Initialize keyboard shortcuts
  function init() {
    document.addEventListener('keydown', handleKeyPress);
    
    // Add visual indicators
    addKeyboardIndicators();
    
    // Setup section-specific features
    setupSectionTheming();
  }

  // Handle keyboard events
  function handleKeyPress(e) {
    // Ignore if in input field
    if (isInputActive()) return;
    
    // Build key combination string
    const key = buildKeyString(e);
    
    // Check for direct shortcuts
    if (shortcuts[key]) {
      e.preventDefault();
      shortcuts[key]();
      return;
    }
    
    // Handle key sequences (like 'g h')
    handleKeySequence(e);
  }

  // Build standardized key string
  function buildKeyString(e) {
    const parts = [];
    if (e.metaKey || e.ctrlKey) parts.push(e.metaKey ? 'cmd' : 'ctrl');
    if (e.altKey) parts.push('alt');
    if (e.shiftKey) parts.push('shift');
    
    // Normalize key name
    let key = e.key.toLowerCase();
    if (key === ' ') key = 'space';
    if (key === 'arrowleft') key = 'left';
    if (key === 'arrowright') key = 'right';
    if (key === 'arrowup') key = 'up';
    if (key === 'arrowdown') key = 'down';
    
    parts.push(key);
    return parts.join('+');
  }

  // Handle multi-key sequences
  function handleKeySequence(e) {
    if (e.key.length === 1 && !e.metaKey && !e.ctrlKey && !e.altKey) {
      keySequence.push(e.key);
      
      clearTimeout(sequenceTimer);
      sequenceTimer = setTimeout(() => {
        keySequence = [];
      }, 500);
      
      const sequence = keySequence.join(' ');
      if (shortcuts[sequence]) {
        e.preventDefault();
        shortcuts[sequence]();
        keySequence = [];
      }
    }
  }

  // Check if input element is active
  function isInputActive() {
    const activeElement = document.activeElement;
    return activeElement && (
      activeElement.tagName === 'INPUT' ||
      activeElement.tagName === 'TEXTAREA' ||
      activeElement.isContentEditable
    );
  }

  // Navigation functions
  function focusSearch() {
    const searchInput = document.querySelector('.md-search__input');
    if (searchInput) {
      searchInput.focus();
      searchInput.select();
    }
  }

  function handleEscape() {
    const searchInput = document.querySelector('.md-search__input');
    if (document.activeElement === searchInput) {
      searchInput.blur();
      document.querySelector('.md-search__form').reset();
    }
  }

  function navigatePrev() {
    const prevLink = document.querySelector('.md-footer__link--prev');
    if (prevLink) prevLink.click();
  }

  function navigateNext() {
    const nextLink = document.querySelector('.md-footer__link--next');
    if (nextLink) nextLink.click();
  }

  function navigateUp() {
    const breadcrumb = document.querySelector('.md-nav__link--active')?.parentElement?.parentElement?.previousElementSibling;
    if (breadcrumb && breadcrumb.tagName === 'A') {
      breadcrumb.click();
    }
  }

  function goHome() {
    window.location.href = '/';
  }

  function goToTags() {
    window.location.href = '/tags/';
  }

  function goToGlossary() {
    window.location.href = '/reference/glossary/';
  }

  // Scrolling functions
  function smoothScroll(distance) {
    window.scrollBy({
      top: distance,
      behavior: 'smooth'
    });
  }

  function jumpToPrevHeading() {
    const headings = Array.from(document.querySelectorAll('h2, h3, h4'));
    const currentScroll = window.scrollY;
    
    for (let i = headings.length - 1; i >= 0; i--) {
      if (headings[i].offsetTop < currentScroll - 10) {
        headings[i].scrollIntoView({ behavior: 'smooth', block: 'start' });
        break;
      }
    }
  }

  function jumpToNextHeading() {
    const headings = Array.from(document.querySelectorAll('h2, h3, h4'));
    const currentScroll = window.scrollY;
    
    for (let heading of headings) {
      if (heading.offsetTop > currentScroll + 10) {
        heading.scrollIntoView({ behavior: 'smooth', block: 'start' });
        break;
      }
    }
  }

  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function scrollToBottom() {
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
  }

  // Theme & Display functions
  function toggleTheme() {
    const toggle = document.querySelector('.md-header__option .md-icon');
    if (toggle) toggle.click();
  }

  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  }

  function toggleSidebar() {
    document.body.classList.toggle('hide-sidebar');
  }

  function toggleTOC() {
    document.body.classList.toggle('hide-toc');
  }

  // Content action functions
  function editPage() {
    const editLink = document.querySelector('.md-content__button.md-icon[title*="Edit"]');
    if (editLink) editLink.click();
  }

  function viewSource() {
    const viewLink = document.querySelector('.md-content__button.md-icon[title*="View"]');
    if (viewLink) viewLink.click();
  }

  function showPageInfo() {
    const info = {
      title: document.title,
      url: window.location.href,
      modified: document.querySelector('meta[name="revised"]')?.content,
      readingTime: calculateReadingTime(),
      wordCount: countWords(),
      headings: document.querySelectorAll('h2, h3').length
    };
    
    showModal('Page Information', formatPageInfo(info));
  }

  function showHelp() {
    window.location.href = '/reference/keyboard-shortcuts/';
  }

  function sharePage() {
    if (navigator.share) {
      navigator.share({
        title: document.title,
        url: window.location.href
      });
    } else {
      // Copy URL to clipboard
      navigator.clipboard.writeText(window.location.href);
      showToast('Link copied to clipboard!');
    }
  }

  // Interactive functions
  function toggleDetails() {
    const focused = document.activeElement;
    if (focused && focused.tagName === 'SUMMARY') {
      focused.click();
    }
  }

  function openSettings() {
    // Placeholder for future settings panel
    showToast('Settings panel coming soon!');
  }

  function openCommandPalette() {
    // Placeholder for future command palette
    showToast('Command palette coming soon!');
  }

  // Helper functions
  function calculateReadingTime() {
    const words = countWords();
    const wpm = 200; // Average reading speed
    return Math.ceil(words / wpm) + ' min read';
  }

  function countWords() {
    const content = document.querySelector('.md-content__inner');
    if (!content) return 0;
    return content.textContent.trim().split(/\s+/).length;
  }

  function formatPageInfo(info) {
    return `
      <dl>
        <dt>Title</dt><dd>${info.title}</dd>
        <dt>URL</dt><dd><code>${info.url}</code></dd>
        <dt>Reading Time</dt><dd>${info.readingTime}</dd>
        <dt>Word Count</dt><dd>${info.wordCount.toLocaleString()}</dd>
        <dt>Sections</dt><dd>${info.headings} headings</dd>
        ${info.modified ? `<dt>Last Modified</dt><dd>${info.modified}</dd>` : ''}
      </dl>
    `;
  }

  // UI Helper functions
  function showModal(title, content) {
    const modal = document.createElement('div');
    modal.className = 'keyboard-modal';
    modal.innerHTML = `
      <div class="keyboard-modal-content">
        <h3>${title}</h3>
        <div>${content}</div>
        <button onclick="this.closest('.keyboard-modal').remove()">Close</button>
      </div>
    `;
    document.body.appendChild(modal);
    
    // Close on Escape
    const closeHandler = (e) => {
      if (e.key === 'Escape') {
        modal.remove();
        document.removeEventListener('keydown', closeHandler);
      }
    };
    document.addEventListener('keydown', closeHandler);
  }

  function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'keyboard-toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.classList.add('show');
    }, 10);
    
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  // Add visual indicators for keyboard shortcuts
  function addKeyboardIndicators() {
    // Add shortcut hints to buttons
    const shortcuts = {
      '.md-search__input': 'cmd+k',
      '.md-footer__link--prev': 'alt+←',
      '.md-footer__link--next': 'alt+→',
      '[data-md-component="palette"] .md-header__option': 't'
    };
    
    Object.entries(shortcuts).forEach(([selector, shortcut]) => {
      const element = document.querySelector(selector);
      if (element) {
        element.setAttribute('data-shortcut', shortcut);
      }
    });
  }

  // Setup section-specific theming
  function setupSectionTheming() {
    const path = window.location.pathname;
    let section = 'default';
    
    if (path.includes('part1-axioms')) section = 'laws';
    else if (path.includes('part2-pillars')) section = 'pillars';
    else if (path.includes('patterns')) section = 'patterns';
    else if (path.includes('case-studies')) section = 'cases';
    else if (path.includes('quantitative')) section = 'quantitative';
    else if (path.includes('reference')) section = 'ref';
    
    document.body.setAttribute('data-section', section);
  }

  // Add required CSS
  const style = document.createElement('style');
  style.textContent = `
    /* Keyboard modal */
    .keyboard-modal {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0,0,0,0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 999;
    }
    
    .keyboard-modal-content {
      background: var(--md-default-bg-color);
      padding: 2rem;
      border-radius: 8px;
      max-width: 500px;
      max-height: 80vh;
      overflow-y: auto;
    }
    
    .keyboard-modal-content dt {
      font-weight: bold;
      margin-top: 1rem;
    }
    
    .keyboard-modal-content dd {
      margin-left: 0;
      margin-bottom: 0.5rem;
    }
    
    /* Keyboard toast */
    .keyboard-toast {
      position: fixed;
      bottom: 2rem;
      left: 50%;
      transform: translateX(-50%) translateY(100px);
      background: var(--md-primary-fg-color);
      color: var(--md-primary-bg-color);
      padding: 1rem 2rem;
      border-radius: 4px;
      z-index: 999;
      transition: transform 0.3s ease;
    }
    
    .keyboard-toast.show {
      transform: translateX(-50%) translateY(0);
    }
    
    /* Shortcut hints */
    [data-shortcut]::after {
      content: attr(data-shortcut);
      position: absolute;
      top: -2rem;
      right: 0;
      padding: 0.25rem 0.5rem;
      background: var(--md-code-bg-color);
      border: 1px solid var(--md-default-fg-color--lightest);
      border-radius: 4px;
      font-size: 0.7rem;
      font-family: var(--md-code-font-family);
      opacity: 0;
      transition: opacity 0.3s ease;
      pointer-events: none;
    }
    
    [data-shortcut]:hover::after {
      opacity: 1;
    }
    
    /* Hide elements */
    body.hide-sidebar .md-sidebar--primary {
      display: none;
    }
    
    body.hide-toc .md-sidebar--secondary {
      display: none;
    }
  `;
  document.head.appendChild(style);

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();