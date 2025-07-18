// Tooltips and Help System
class TooltipsHelp {
  constructor() {
    this.tooltips = new Map();
    this.helpPanel = null;
    this.contextHelp = new Map();
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
    // Create help button
    this.createHelpButton();
    
    // Create help panel
    this.createHelpPanel();
    
    // Initialize tooltips
    this.initializeTooltips();
    
    // Set up context-sensitive help
    this.setupContextHelp();
    
    // Add keyboard shortcuts
    this.setupKeyboardShortcuts();
  }
  
  createHelpButton() {
    const helpButton = document.createElement('button');
    helpButton.className = 'help-button';
    helpButton.innerHTML = `
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <circle cx="12" cy="12" r="10"></circle>
        <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
        <line x1="12" y1="17" x2="12.01" y2="17"></line>
      </svg>
    `;
    helpButton.setAttribute('title', 'Help (F1)');
    
    helpButton.addEventListener('click', () => this.toggleHelp());
    
    document.body.appendChild(helpButton);
  }
  
  createHelpPanel() {
    const panel = document.createElement('div');
    panel.className = 'help-panel';
    panel.innerHTML = `
      <div class="help-panel-header">
        <h3>Help & Documentation</h3>
        <button class="help-close">×</button>
      </div>
      
      <div class="help-panel-content">
        <div class="help-search">
          <input type="text" placeholder="Search help..." class="help-search-input">
        </div>
        
        <div class="help-sections">
          <div class="help-section">
            <h4>🎯 Quick Start</h4>
            <ul>
              <li><a href="#navigation">Navigation Tips</a></li>
              <li><a href="#tools">Using Interactive Tools</a></li>
              <li><a href="#shortcuts">Keyboard Shortcuts</a></li>
              <li><a href="#glossary">Glossary Terms</a></li>
            </ul>
          </div>
          
          <div class="help-section" id="navigation">
            <h4>📍 Navigation</h4>
            <p>Navigate through the content using:</p>
            <ul>
              <li><strong>Left sidebar</strong>: Main sections and chapters</li>
              <li><strong>Breadcrumbs</strong>: Current location path</li>
              <li><strong>Next/Previous</strong>: Sequential reading</li>
              <li><strong>Search (Ctrl+K)</strong>: Find specific topics</li>
            </ul>
          </div>
          
          <div class="help-section" id="tools">
            <h4>🛠️ Interactive Tools</h4>
            <p>Each tool has interactive features:</p>
            <ul>
              <li><strong>Calculators</strong>: Enter values and see real-time results</li>
              <li><strong>Visualizers</strong>: Click/drag to interact with diagrams</li>
              <li><strong>Scenarios</strong>: Run simulations to understand concepts</li>
              <li><strong>Examples</strong>: Hover for additional information</li>
            </ul>
          </div>
          
          <div class="help-section" id="shortcuts">
            <h4>⌨️ Keyboard Shortcuts</h4>
            <dl class="shortcuts-list">
              <dt><kbd>F1</kbd></dt>
              <dd>Toggle this help panel</dd>
              
              <dt><kbd>Ctrl</kbd> + <kbd>K</kbd></dt>
              <dd>Search documentation</dd>
              
              <dt><kbd>/</kbd></dt>
              <dd>Quick search</dd>
              
              <dt><kbd>N</kbd></dt>
              <dd>Next page</dd>
              
              <dt><kbd>P</kbd></dt>
              <dd>Previous page</dd>
              
              <dt><kbd>.</kbd></dt>
              <dd>Show source</dd>
              
              <dt><kbd>Esc</kbd></dt>
              <dd>Close dialogs</dd>
            </dl>
          </div>
          
          <div class="help-section" id="glossary">
            <h4>📚 Common Terms</h4>
            <dl class="glossary-list">
              <dt>Latency</dt>
              <dd>Time delay between request and response</dd>
              
              <dt>Throughput</dt>
              <dd>Number of operations per unit time</dd>
              
              <dt>CAP Theorem</dt>
              <dd>Trade-off between Consistency, Availability, and Partition tolerance</dd>
              
              <dt>Consensus</dt>
              <dd>Agreement among distributed nodes</dd>
              
              <dt>Quorum</dt>
              <dd>Minimum nodes needed for operation</dd>
            </dl>
            <a href="../reference/glossary/" class="help-link">View Full Glossary →</a>
          </div>
          
          <div class="help-section">
            <h4>💡 Tips</h4>
            <div class="help-tips">
              <div class="help-tip">
                <span class="tip-icon">💡</span>
                <p>Hover over technical terms to see definitions</p>
              </div>
              <div class="help-tip">
                <span class="tip-icon">🎨</span>
                <p>Use the theme toggle for dark/light mode</p>
              </div>
              <div class="help-tip">
                <span class="tip-icon">📱</span>
                <p>The site is mobile-friendly - swipe to navigate</p>
              </div>
              <div class="help-tip">
                <span class="tip-icon">🔍</span>
                <p>Use browser zoom (Ctrl +/-) for readability</p>
              </div>
            </div>
          </div>
        </div>
        
        <div class="help-context" id="help-context">
          <h4>📍 Current Page Help</h4>
          <div id="context-help-content">
            <p>Navigate to any page to see context-specific help here.</p>
          </div>
        </div>
      </div>
      
      <div class="help-panel-footer">
        <a href="https://github.com/deepaucksharma/DStudio/issues" target="_blank" class="help-link">
          Report an Issue
        </a>
        <a href="../introduction/how-to-use/" class="help-link">
          Full Guide
        </a>
      </div>
    `;
    
    document.body.appendChild(panel);
    this.helpPanel = panel;
    
    // Close button
    panel.querySelector('.help-close').addEventListener('click', () => this.toggleHelp());
    
    // Search functionality
    const searchInput = panel.querySelector('.help-search-input');
    searchInput.addEventListener('input', (e) => this.searchHelp(e.target.value));
    
    // Smooth scroll for anchor links
    panel.querySelectorAll('a[href^="#"]').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const target = panel.querySelector(e.target.getAttribute('href'));
        if (target) {
          target.scrollIntoView({ behavior: 'smooth' });
        }
      });
    });
  }
  
  initializeTooltips() {
    // Define tooltips for common terms
    const tooltipDefinitions = {
      'latency': 'The time delay between a request and its response',
      'throughput': 'The number of operations processed per unit of time',
      'consistency': 'The property that all nodes see the same data at the same time',
      'availability': 'The ability of a system to remain operational',
      'partition': 'A network failure that separates nodes',
      'cap theorem': 'States that distributed systems can guarantee only 2 of 3: Consistency, Availability, Partition tolerance',
      'consensus': 'Agreement among distributed nodes on a value or state',
      'quorum': 'The minimum number of nodes needed to proceed with an operation',
      'replication': 'Copying data across multiple nodes for reliability',
      'sharding': 'Splitting data across multiple nodes for scalability',
      'eventual consistency': 'Nodes will become consistent over time',
      'strong consistency': 'All nodes see the same data immediately',
      'byzantine failure': 'A node that behaves arbitrarily or maliciously',
      'split brain': 'When a cluster divides into multiple parts that act independently',
      'leader election': 'Process of choosing a coordinator node',
      'vector clock': 'Data structure for tracking causality in distributed systems',
      'crdt': 'Conflict-free Replicated Data Type - data structures that converge automatically',
      'raft': 'A consensus algorithm designed for understandability',
      'paxos': 'A family of consensus protocols',
      'two-phase commit': 'Protocol for atomic distributed transactions',
      'gossip protocol': 'Peer-to-peer communication pattern for spreading information',
      'circuit breaker': 'Pattern to prevent cascading failures',
      'backpressure': 'Flow control mechanism to prevent overload',
      'idempotent': 'Operations that can be applied multiple times without changing the result',
      'linearizability': 'Strongest consistency guarantee - operations appear instantaneous',
      'serializability': 'Guarantee that concurrent operations have a serial equivalent',
      'acid': 'Atomicity, Consistency, Isolation, Durability - database properties',
      'base': 'Basically Available, Soft state, Eventual consistency - alternative to ACID',
      'saga': 'Pattern for managing distributed transactions',
      'cqrs': 'Command Query Responsibility Segregation - separating reads and writes',
      'event sourcing': 'Storing state changes as a sequence of events'
    };
    
    // Store definitions
    tooltipDefinitions.forEach((definition, term) => {
      this.tooltips.set(term.toLowerCase(), definition);
    });
    
    // Add tooltips to existing elements
    this.addTooltipsToContent();
    
    // Watch for content changes
    const observer = new MutationObserver(() => {
      this.addTooltipsToContent();
    });
    
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }
  
  addTooltipsToContent() {
    // Find all text nodes containing tooltip terms
    const textNodes = this.getTextNodes(document.querySelector('.md-content') || document.body);
    
    textNodes.forEach(node => {
      const text = node.textContent;
      let hasMatch = false;
      
      // Check if text contains any tooltip terms
      this.tooltips.forEach((definition, term) => {
        const regex = new RegExp(`\\b${term}\\b`, 'gi');
        if (regex.test(text)) {
          hasMatch = true;
        }
      });
      
      if (hasMatch && node.parentNode.tagName !== 'SPAN' && 
          !node.parentNode.classList.contains('tooltip-term')) {
        // Wrap matching terms in tooltip spans
        const span = document.createElement('span');
        span.innerHTML = this.highlightTerms(text);
        node.parentNode.replaceChild(span, node);
      }
    });
    
    // Add event listeners to tooltip terms
    document.querySelectorAll('.tooltip-term').forEach(term => {
      if (!term.hasAttribute('data-tooltip-initialized')) {
        term.setAttribute('data-tooltip-initialized', 'true');
        
        term.addEventListener('mouseenter', (e) => this.showTooltip(e));
        term.addEventListener('mouseleave', () => this.hideTooltip());
        term.addEventListener('focus', (e) => this.showTooltip(e));
        term.addEventListener('blur', () => this.hideTooltip());
      }
    });
  }
  
  getTextNodes(element) {
    const textNodes = [];
    const walker = document.createTreeWalker(
      element,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode: (node) => {
          // Skip script, style, and already processed nodes
          const parent = node.parentNode;
          if (parent.tagName === 'SCRIPT' || 
              parent.tagName === 'STYLE' || 
              parent.tagName === 'CODE' ||
              parent.classList.contains('tooltip-term')) {
            return NodeFilter.FILTER_REJECT;
          }
          return node.textContent.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
        }
      }
    );
    
    let node;
    while (node = walker.nextNode()) {
      textNodes.push(node);
    }
    
    return textNodes;
  }
  
  highlightTerms(text) {
    let result = text;
    
    // Sort terms by length (longest first) to avoid partial matches
    const sortedTerms = Array.from(this.tooltips.keys()).sort((a, b) => b.length - a.length);
    
    sortedTerms.forEach(term => {
      const regex = new RegExp(`\\b(${term})\\b`, 'gi');
      result = result.replace(regex, '<span class="tooltip-term">$1</span>');
    });
    
    return result;
  }
  
  showTooltip(event) {
    const term = event.target.textContent.toLowerCase();
    const definition = this.tooltips.get(term);
    
    if (!definition) return;
    
    // Remove existing tooltip
    this.hideTooltip();
    
    // Create tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip-popup';
    tooltip.innerHTML = `
      <div class="tooltip-content">
        <strong>${term}</strong>
        <p>${definition}</p>
      </div>
      <div class="tooltip-arrow"></div>
    `;
    
    document.body.appendChild(tooltip);
    
    // Position tooltip
    const rect = event.target.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    let left = rect.left + (rect.width - tooltipRect.width) / 2;
    let top = rect.top - tooltipRect.height - 10;
    
    // Adjust if tooltip goes off screen
    if (left < 10) left = 10;
    if (left + tooltipRect.width > window.innerWidth - 10) {
      left = window.innerWidth - tooltipRect.width - 10;
    }
    
    if (top < 10) {
      // Show below instead
      top = rect.bottom + 10;
      tooltip.classList.add('tooltip-below');
    }
    
    tooltip.style.left = `${left}px`;
    tooltip.style.top = `${top}px`;
    
    // Fade in
    setTimeout(() => tooltip.classList.add('tooltip-visible'), 10);
  }
  
  hideTooltip() {
    const tooltip = document.querySelector('.tooltip-popup');
    if (tooltip) {
      tooltip.remove();
    }
  }
  
  setupContextHelp() {
    // Define context-specific help for different page types
    this.contextHelp.set('latency-calculator', {
      title: 'Latency Calculator Help',
      content: `
        <p>Calculate network latency based on distance and medium.</p>
        <h5>How to use:</h5>
        <ol>
          <li>Select two locations or enter custom distance</li>
          <li>Choose the network medium (fiber, copper, wireless)</li>
          <li>Add network hops and processing delays</li>
          <li>View the total latency breakdown</li>
        </ol>
        <p><strong>Tip:</strong> Remember that this shows theoretical minimum latency. Real-world values are typically 20-50% higher.</p>
      `
    });
    
    this.contextHelp.set('capacity-planner', {
      title: 'Capacity Planner Help',
      content: `
        <p>Plan system capacity using Little's Law and queueing theory.</p>
        <h5>Key concepts:</h5>
        <ul>
          <li><strong>Arrival Rate:</strong> Requests per second</li>
          <li><strong>Service Time:</strong> Time to process one request</li>
          <li><strong>Utilization:</strong> % of capacity in use</li>
          <li><strong>Queue Length:</strong> Average waiting requests</li>
        </ul>
        <p><strong>Warning:</strong> Keep utilization below 80% for stable performance.</p>
      `
    });
    
    this.contextHelp.set('consistency-visualizer', {
      title: 'Consistency Visualizer Help',
      content: `
        <p>Explore different consistency models and their trade-offs.</p>
        <h5>Consistency Models:</h5>
        <ul>
          <li><strong>Strong:</strong> All nodes see same data immediately</li>
          <li><strong>Eventual:</strong> Nodes converge over time</li>
          <li><strong>Causal:</strong> Preserves cause-effect relationships</li>
          <li><strong>Weak:</strong> No ordering guarantees</li>
        </ul>
        <p><strong>Try:</strong> Run different scenarios to see how each model behaves under failure conditions.</p>
      `
    });
    
    this.contextHelp.set('cap-explorer', {
      title: 'CAP Theorem Explorer Help',
      content: `
        <p>Understand the CAP theorem through interactive examples.</p>
        <h5>The Three Properties:</h5>
        <ul>
          <li><strong>C:</strong> Consistency - All nodes have same data</li>
          <li><strong>A:</strong> Availability - System stays operational</li>
          <li><strong>P:</strong> Partition Tolerance - Handles network splits</li>
        </ul>
        <p><strong>Remember:</strong> You can only guarantee 2 out of 3 properties during network partitions.</p>
      `
    });
    
    // Update context help when page changes
    this.updateContextHelp();
    
    // Watch for navigation
    const observer = new MutationObserver(() => {
      this.updateContextHelp();
    });
    
    observer.observe(document.querySelector('.md-content') || document.body, {
      childList: true,
      subtree: true
    });
  }
  
  updateContextHelp() {
    const contextContent = document.getElementById('context-help-content');
    if (!contextContent) return;
    
    // Determine current page context
    const path = window.location.pathname;
    let contextKey = null;
    
    if (path.includes('latency-calculator')) {
      contextKey = 'latency-calculator';
    } else if (path.includes('capacity-planner')) {
      contextKey = 'capacity-planner';
    } else if (path.includes('consistency-visualizer')) {
      contextKey = 'consistency-visualizer';
    } else if (path.includes('cap-explorer')) {
      contextKey = 'cap-explorer';
    }
    
    if (contextKey && this.contextHelp.has(contextKey)) {
      const help = this.contextHelp.get(contextKey);
      contextContent.innerHTML = `
        <h5>${help.title}</h5>
        ${help.content}
      `;
    } else {
      // Generic help for current page
      const pageTitle = document.querySelector('h1')?.textContent || 'Current Page';
      contextContent.innerHTML = `
        <h5>${pageTitle}</h5>
        <p>This page covers ${pageTitle.toLowerCase()}. Use the navigation to explore related topics.</p>
        <p><strong>Tip:</strong> Look for interactive elements marked with 🔍 or ▶️ symbols.</p>
      `;
    }
  }
  
  setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // F1 - Toggle help
      if (e.key === 'F1') {
        e.preventDefault();
        this.toggleHelp();
      }
      
      // Escape - Close help
      if (e.key === 'Escape' && this.helpPanel.classList.contains('help-visible')) {
        this.toggleHelp();
      }
      
      // ? - Show help (when not in input)
      if (e.key === '?' && !this.isInputElement(e.target)) {
        e.preventDefault();
        this.toggleHelp();
      }
    });
  }
  
  isInputElement(element) {
    const inputTags = ['INPUT', 'TEXTAREA', 'SELECT'];
    return inputTags.includes(element.tagName) || element.contentEditable === 'true';
  }
  
  toggleHelp() {
    this.helpPanel.classList.toggle('help-visible');
    document.body.classList.toggle('help-open');
    
    // Update context help when opening
    if (this.helpPanel.classList.contains('help-visible')) {
      this.updateContextHelp();
      
      // Focus search input
      setTimeout(() => {
        this.helpPanel.querySelector('.help-search-input').focus();
      }, 300);
    }
  }
  
  searchHelp(query) {
    const sections = this.helpPanel.querySelectorAll('.help-section');
    const searchTerm = query.toLowerCase();
    
    if (!searchTerm) {
      // Show all sections
      sections.forEach(section => {
        section.style.display = 'block';
      });
      return;
    }
    
    // Filter sections
    sections.forEach(section => {
      const text = section.textContent.toLowerCase();
      if (text.includes(searchTerm)) {
        section.style.display = 'block';
        
        // Highlight matching text
        this.highlightSearchTerm(section, searchTerm);
      } else {
        section.style.display = 'none';
      }
    });
  }
  
  highlightSearchTerm(element, term) {
    // Simple highlight implementation
    const walker = document.createTreeWalker(
      element,
      NodeFilter.SHOW_TEXT,
      null,
      false
    );
    
    const textNodes = [];
    let node;
    while (node = walker.nextNode()) {
      textNodes.push(node);
    }
    
    textNodes.forEach(node => {
      const text = node.textContent;
      const regex = new RegExp(`(${term})`, 'gi');
      if (regex.test(text)) {
        const span = document.createElement('span');
        span.innerHTML = text.replace(regex, '<mark>$1</mark>');
        node.parentNode.replaceChild(span, node);
      }
    });
  }
}

// Initialize tooltips and help system
const tooltipsHelp = new TooltipsHelp();