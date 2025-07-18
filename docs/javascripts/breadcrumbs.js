// Enhanced Breadcrumb Navigation
class BreadcrumbNav {
  constructor() {
    this.nameMap = {
      'part1-axioms': 'Part I: Axioms',
      'part2-pillars': 'Part II: Pillars',
      'part4-case-study': 'Part IV: Case Study',
      'part5-capstone': 'Part V: Capstone',
      'part6-advanced': 'Part VI: Advanced',
      'axiom-1-latency': 'Axiom 1: Latency',
      'axiom-2-capacity': 'Axiom 2: Capacity',
      'axiom-3-failure': 'Axiom 3: Failure',
      'axiom-4-concurrency': 'Axiom 4: Concurrency',
      'axiom-5-coordination': 'Axiom 5: Coordination',
      'axiom-6-observability': 'Axiom 6: Observability',
      'axiom-7-human-interface': 'Axiom 7: Human Interface',
      'axiom-8-economics': 'Axiom 8: Economics',
      'pillar-1-work': 'Pillar 1: Work',
      'pillar-2-state': 'Pillar 2: State',
      'pillar-3-truth': 'Pillar 3: Truth',
      'pillar-4-control': 'Pillar 4: Control',
      'pillar-5-intelligence': 'Pillar 5: Intelligence',
      'pillar-6-trust': 'Pillar 6: Trust',
      'introduction': 'Getting Started',
      'tools': 'Interactive Tools',
      'reference': 'Reference',
      'latency-calculator': 'Latency Calculator',
      'capacity-planner': 'Capacity Planner',
      'consistency-visualizer': 'Consistency Visualizer',
      'cap-explorer': 'CAP Explorer'
    };
    
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
    // Don't add breadcrumbs on the home page
    if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
      return;
    }
    
    const breadcrumbContainer = this.createBreadcrumbContainer();
    const mainContent = document.querySelector('.md-content');
    
    if (mainContent && mainContent.firstChild) {
      mainContent.insertBefore(breadcrumbContainer, mainContent.firstChild);
    }
    
    this.updateBreadcrumbs();
    
    // Update on navigation
    const observer = new MutationObserver(() => {
      this.updateBreadcrumbs();
    });
    
    const target = document.querySelector('.md-content');
    if (target) {
      observer.observe(target, { childList: true, subtree: true });
    }
  }
  
  createBreadcrumbContainer() {
    const container = document.createElement('nav');
    container.className = 'breadcrumb-nav';
    return container;
  }
  
  updateBreadcrumbs() {
    const container = document.querySelector('.breadcrumb-nav');
    if (!container) return;
    
    const path = window.location.pathname;
    const segments = path.split('/').filter(s => s && s !== 'index.html');
    
    // Build breadcrumb data
    const breadcrumbs = this.buildBreadcrumbData(segments);
    
    // Generate HTML
    let breadcrumbHTML = '<ol class="breadcrumb-list">';
    
    breadcrumbs.forEach((crumb, index) => {
      const isLast = index === breadcrumbs.length - 1;
      
      if (isLast) {
        breadcrumbHTML += `
          <li class="breadcrumb-item active">
            <span class="breadcrumb-text">${crumb.name}</span>
          </li>
        `;
      } else {
        breadcrumbHTML += `
          <li class="breadcrumb-item">
            <a href="${crumb.path}" class="breadcrumb-link">${crumb.name}</a>
            <span class="breadcrumb-separator">›</span>
          </li>
        `;
      }
    });
    
    breadcrumbHTML += '</ol>';
    
    // Add structured data for SEO
    const structuredData = this.generateStructuredData(breadcrumbs);
    breadcrumbHTML += structuredData;
    
    container.innerHTML = breadcrumbHTML;
  }
  
  buildBreadcrumbData(segments) {
    const breadcrumbs = [
      { name: 'Home', path: '/' }
    ];
    
    let currentPath = '';
    segments.forEach((segment, index) => {
      currentPath += `/${segment}`;
      
      // Skip index files
      if (segment === 'index.html' || segment === 'index.md') {
        return;
      }
      
      const name = this.formatSegmentName(segment);
      breadcrumbs.push({
        name: name,
        path: currentPath + '/'
      });
    });
    
    // Get current page title if available
    const pageTitle = document.querySelector('h1');
    if (pageTitle && breadcrumbs.length > 1) {
      breadcrumbs[breadcrumbs.length - 1].name = pageTitle.textContent;
    }
    
    return breadcrumbs;
  }
  
  formatSegmentName(segment) {
    // Check name map first
    if (this.nameMap[segment]) {
      return this.nameMap[segment];
    }
    
    // Format generic segments
    return segment
      .replace(/-/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase())
      .replace(/\bAnd\b/g, 'and')
      .replace(/\bOf\b/g, 'of')
      .replace(/\bThe\b/g, 'the');
  }
  
  generateStructuredData(breadcrumbs) {
    const items = breadcrumbs.map((crumb, index) => ({
      "@type": "ListItem",
      "position": index + 1,
      "name": crumb.name,
      "item": window.location.origin + crumb.path
    }));
    
    const structuredData = {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": items
    };
    
    return `
      <script type="application/ld+json">
        ${JSON.stringify(structuredData, null, 2)}
      </script>
    `;
  }
}

// Initialize breadcrumbs
const breadcrumbNav = new BreadcrumbNav();