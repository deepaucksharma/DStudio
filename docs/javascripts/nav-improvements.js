// Navigation Improvements - Auto-scroll and enhancements
class NavigationEnhancements {
  constructor() {
    this.init();
  }
  
  init() {
    // Auto-scroll active item into view
    this.scrollActiveIntoView();
    
    // Monitor navigation changes
    this.observeNavChanges();
  }
  
  scrollActiveIntoView() {
    const activeLink = document.querySelector('.md-nav__link--active');
    if (!activeLink) return;
    
    const sidebar = activeLink.closest('.md-sidebar__scrollwrap');
    if (!sidebar) return;
    
    // Get positions
    const linkRect = activeLink.getBoundingClientRect();
    const sidebarRect = sidebar.getBoundingClientRect();
    
    // Check if link is outside visible area
    if (linkRect.top < sidebarRect.top || linkRect.bottom > sidebarRect.bottom) {
      // Scroll the active item to the center of the sidebar
      activeLink.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
      });
    }
  }
  
  observeNavChanges() {
    // Watch for navigation changes (page loads via instant navigation)
    const observer = new MutationObserver(() => {
      this.scrollActiveIntoView();
    });
    
    const sidebar = document.querySelector('.md-sidebar--primary');
    if (sidebar) {
      observer.observe(sidebar, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['class']
      });
    }
  }
}

// Search Overlay Improvements
class SearchOverlayFix {
  constructor() {
    this.init();
  }
  
  init() {
    // Get search toggle
    const searchToggle = document.querySelector('[data-md-toggle="search"]');
    if (!searchToggle) return;
    
    searchToggle.addEventListener('change', (e) => {
      if (e.target.checked) {
        this.enableSearchMode();
      } else {
        this.disableSearchMode();
      }
    });
  }
  
  enableSearchMode() {
    // Disable body scroll
    document.body.style.overflow = 'hidden';
    
    // Add class for full-width modal styling
    document.body.classList.add('search-modal-open');
  }
  
  disableSearchMode() {
    // Re-enable body scroll
    document.body.style.overflow = '';
    
    // Remove modal class
    document.body.classList.remove('search-modal-open');
  }
}

// Quick Navigation Shortcuts
class QuickNavigation {
  constructor() {
    this.shortcuts = new Map();
    this.commandPalette = null;
    this.init();
  }
  
  init() {
    this.registerShortcuts();
    this.createCommandPalette();
    this.attachKeyboardListeners();
    this.addQuickJump();
  }
  
  registerShortcuts() {
    // Navigation shortcuts
    this.shortcuts.set('g h', { action: () => this.navigateTo('/'), description: 'Go to Home' });
    this.shortcuts.set('g a', { action: () => this.navigateTo('/part1-axioms/'), description: 'Go to Axioms' });
    this.shortcuts.set('g p', { action: () => this.navigateTo('/part2-pillars/'), description: 'Go to Pillars' });
    this.shortcuts.set('g t', { action: () => this.navigateTo('/tools/'), description: 'Go to Tools' });
    this.shortcuts.set('g r', { action: () => this.navigateTo('/reference/'), description: 'Go to Reference' });
    
    // Page navigation
    this.shortcuts.set('j', { action: () => this.scrollBy(100), description: 'Scroll down' });
    this.shortcuts.set('k', { action: () => this.scrollBy(-100), description: 'Scroll up' });
    this.shortcuts.set('n', { action: () => this.nextPage(), description: 'Next page' });
    this.shortcuts.set('p', { action: () => this.previousPage(), description: 'Previous page' });
    
    // Features
    this.shortcuts.set('/', { action: () => this.focusSearch(), description: 'Focus search' });
    this.shortcuts.set('?', { action: () => this.showShortcuts(), description: 'Show shortcuts' });
    this.shortcuts.set('cmd+k', { action: () => this.toggleCommandPalette(), description: 'Command palette' });
    this.shortcuts.set('ctrl+k', { action: () => this.toggleCommandPalette(), description: 'Command palette' });
    
    // Section jumps
    this.shortcuts.set('1', { action: () => this.jumpToSection(0), description: 'Jump to section 1' });
    this.shortcuts.set('2', { action: () => this.jumpToSection(1), description: 'Jump to section 2' });
    this.shortcuts.set('3', { action: () => this.jumpToSection(2), description: 'Jump to section 3' });
    this.shortcuts.set('4', { action: () => this.jumpToSection(3), description: 'Jump to section 4' });
    this.shortcuts.set('5', { action: () => this.jumpToSection(4), description: 'Jump to section 5' });
  }
  
  createCommandPalette() {
    const palette = document.createElement('div');
    palette.className = 'command-palette';
    palette.innerHTML = `
      <div class="command-palette-backdrop"></div>
      <div class="command-palette-modal">
        <div class="command-palette-header">
          <input type="text" class="command-palette-input" placeholder="Type a command or search..." />
          <button class="command-palette-close">×</button>
        </div>
        <div class="command-palette-results"></div>
        <div class="command-palette-footer">
          <span><kbd>↑↓</kbd> Navigate</span>
          <span><kbd>Enter</kbd> Select</span>
          <span><kbd>Esc</kbd> Close</span>
        </div>
      </div>
    `;
    
    document.body.appendChild(palette);
    this.commandPalette = palette;
    
    // Set up event listeners
    const backdrop = palette.querySelector('.command-palette-backdrop');
    const closeBtn = palette.querySelector('.command-palette-close');
    const input = palette.querySelector('.command-palette-input');
    
    backdrop.addEventListener('click', () => this.toggleCommandPalette());
    closeBtn.addEventListener('click', () => this.toggleCommandPalette());
    input.addEventListener('input', (e) => this.filterCommands(e.target.value));
    
    // Keyboard navigation
    input.addEventListener('keydown', (e) => this.handleCommandNavigation(e));
  }
  
  attachKeyboardListeners() {
    let keys = [];
    let keyTimer = null;
    
    document.addEventListener('keydown', (e) => {
      // Ignore if typing in input
      if (this.isInputElement(e.target)) return;
      
      // Handle modifier keys
      const key = this.getKeyString(e);
      
      // Check single key shortcuts
      if (this.shortcuts.has(key) && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        this.shortcuts.get(key).action();
        return;
      }
      
      // Check command shortcuts
      if (this.shortcuts.has(key)) {
        e.preventDefault();
        this.shortcuts.get(key).action();
        return;
      }
      
      // Build key sequence
      keys.push(e.key.toLowerCase());
      clearTimeout(keyTimer);
      
      // Check sequence
      const sequence = keys.join(' ');
      if (this.shortcuts.has(sequence)) {
        e.preventDefault();
        this.shortcuts.get(sequence).action();
        keys = [];
      } else {
        // Reset after delay
        keyTimer = setTimeout(() => {
          keys = [];
        }, 500);
      }
    });
  }
  
  addQuickJump() {
    // Add section markers
    const headings = document.querySelectorAll('.md-content h2, .md-content h3');
    headings.forEach((heading, index) => {
      const marker = document.createElement('span');
      marker.className = 'section-marker';
      marker.textContent = `§${index + 1}`;
      marker.setAttribute('title', `Press ${index + 1} to jump here`);
      heading.insertBefore(marker, heading.firstChild);
    });
  }
  
  // Helper methods
  navigateTo(path) {
    window.location.href = path;
  }
  
  scrollBy(amount) {
    window.scrollBy({ top: amount, behavior: 'smooth' });
  }
  
  nextPage() {
    const nextLink = document.querySelector('.md-footer__link--next');
    if (nextLink) nextLink.click();
  }
  
  previousPage() {
    const prevLink = document.querySelector('.md-footer__link--prev');
    if (prevLink) prevLink.click();
  }
  
  focusSearch() {
    const searchToggle = document.querySelector('[data-md-toggle="search"]');
    if (searchToggle) {
      searchToggle.checked = true;
      searchToggle.dispatchEvent(new Event('change'));
      setTimeout(() => {
        const searchInput = document.querySelector('.md-search__input');
        if (searchInput) searchInput.focus();
      }, 100);
    }
  }
  
  jumpToSection(index) {
    const headings = document.querySelectorAll('.md-content h2, .md-content h3');
    if (headings[index]) {
      headings[index].scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
  
  showShortcuts() {
    this.toggleCommandPalette();
    setTimeout(() => {
      const input = this.commandPalette.querySelector('.command-palette-input');
      input.value = 'shortcuts';
      this.filterCommands('shortcuts');
    }, 100);
  }
  
  toggleCommandPalette() {
    const isOpen = this.commandPalette.classList.toggle('open');
    
    if (isOpen) {
      // Populate initial commands
      this.populateCommands();
      
      // Focus input
      const input = this.commandPalette.querySelector('.command-palette-input');
      input.value = '';
      input.focus();
      
      // Disable body scroll
      document.body.style.overflow = 'hidden';
    } else {
      // Re-enable body scroll
      document.body.style.overflow = '';
    }
  }
  
  populateCommands() {
    const results = this.commandPalette.querySelector('.command-palette-results');
    
    // Get all available commands
    const commands = [
      ...Array.from(this.shortcuts.entries()).map(([key, value]) => ({
        type: 'shortcut',
        key,
        ...value
      })),
      ...this.getPageCommands()
    ];
    
    results.innerHTML = commands.map((cmd, index) => `
      <div class="command-item ${index === 0 ? 'selected' : ''}" data-index="${index}">
        ${cmd.type === 'shortcut' ? `<kbd class="command-key">${cmd.key}</kbd>` : `<span class="command-icon">${cmd.icon || '📄'}</span>`}
        <span class="command-text">${cmd.description || cmd.title}</span>
      </div>
    `).join('');
    
    // Add click handlers
    results.querySelectorAll('.command-item').forEach(item => {
      item.addEventListener('click', () => {
        const index = parseInt(item.dataset.index);
        this.executeCommand(commands[index]);
      });
    });
  }
  
  getPageCommands() {
    const commands = [];
    
    // Add page navigation
    document.querySelectorAll('.md-nav__link').forEach(link => {
      const text = link.textContent.trim();
      const href = link.getAttribute('href');
      if (text && href) {
        commands.push({
          type: 'page',
          title: text,
          action: () => window.location.href = href,
          icon: '📄'
        });
      }
    });
    
    return commands;
  }
  
  filterCommands(query) {
    const results = this.commandPalette.querySelector('.command-palette-results');
    const items = results.querySelectorAll('.command-item');
    
    items.forEach(item => {
      const text = item.textContent.toLowerCase();
      if (text.includes(query.toLowerCase())) {
        item.style.display = 'flex';
      } else {
        item.style.display = 'none';
      }
    });
    
    // Select first visible item
    const visible = Array.from(items).find(item => item.style.display !== 'none');
    if (visible) {
      items.forEach(item => item.classList.remove('selected'));
      visible.classList.add('selected');
    }
  }
  
  handleCommandNavigation(e) {
    const results = this.commandPalette.querySelector('.command-palette-results');
    const items = Array.from(results.querySelectorAll('.command-item')).filter(
      item => item.style.display !== 'none'
    );
    const selected = results.querySelector('.selected');
    const currentIndex = items.indexOf(selected);
    
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        if (currentIndex < items.length - 1) {
          selected.classList.remove('selected');
          items[currentIndex + 1].classList.add('selected');
          items[currentIndex + 1].scrollIntoView({ block: 'nearest' });
        }
        break;
        
      case 'ArrowUp':
        e.preventDefault();
        if (currentIndex > 0) {
          selected.classList.remove('selected');
          items[currentIndex - 1].classList.add('selected');
          items[currentIndex - 1].scrollIntoView({ block: 'nearest' });
        }
        break;
        
      case 'Enter':
        e.preventDefault();
        if (selected) {
          selected.click();
        }
        break;
        
      case 'Escape':
        e.preventDefault();
        this.toggleCommandPalette();
        break;
    }
  }
  
  executeCommand(command) {
    this.toggleCommandPalette();
    if (command.action) {
      command.action();
    }
  }
  
  isInputElement(element) {
    const inputTags = ['INPUT', 'TEXTAREA', 'SELECT'];
    return inputTags.includes(element.tagName) || element.contentEditable === 'true';
  }
  
  getKeyString(e) {
    const parts = [];
    if (e.ctrlKey) parts.push('ctrl');
    if (e.metaKey) parts.push('cmd');
    if (e.altKey) parts.push('alt');
    if (e.shiftKey) parts.push('shift');
    
    const key = e.key.toLowerCase();
    if (key !== 'control' && key !== 'meta' && key !== 'alt' && key !== 'shift') {
      parts.push(key);
    }
    
    return parts.join('+');
  }
}

// Initialize enhancements
document.addEventListener('DOMContentLoaded', () => {
  new NavigationEnhancements();
  new SearchOverlayFix();
  new QuickNavigation();
});