/* ===================================
   Consolidated Breadcrumb Navigation
   Combines traditional breadcrumbs with learning path progress
   =================================== */

class BreadcrumbNavigation {
  constructor() {
    this.currentPath = window.location.pathname;
    this.learningPaths = this.defineLearningPaths();
    this.init();
  }
  
  defineLearningPaths() {
    return {
      axioms: {
        name: 'Axioms Path',
        steps: [
          { path: '/part1-axioms/', label: 'Overview' },
          { path: '/part1-axioms/axiom-1-latency/', label: 'Latency' },
          { path: '/part1-axioms/axiom-2-capacity/', label: 'Capacity' },
          { path: '/part1-axioms/axiom-3-failure/', label: 'Failure' },
          { path: '/part1-axioms/axiom-4-concurrency/', label: 'Concurrency' },
          { path: '/part1-axioms/axiom-5-coordination/', label: 'Coordination' },
          { path: '/part1-axioms/axiom-6-observability/', label: 'Observability' },
          { path: '/part1-axioms/axiom-7-human-interface/', label: 'Human Interface' },
          { path: '/part1-axioms/axiom-8-economics/', label: 'Economics' }
        ]
      },
      pillars: {
        name: 'Pillars Path',
        steps: [
          { path: '/part2-pillars/', label: 'Overview' },
          { path: '/part2-pillars/pillar-1-work/', label: 'Work Distribution' },
          { path: '/part2-pillars/pillar-2-state/', label: 'State Distribution' },
          { path: '/part2-pillars/pillar-3-truth/', label: 'Truth Distribution' },
          { path: '/part2-pillars/pillar-4-control/', label: 'Control Distribution' },
          { path: '/part2-pillars/pillar-5-intelligence/', label: 'Intelligence Distribution' },
          { path: '/part2-pillars/pillar-6-trust/', label: 'Trust Distribution' }
        ]
      },
      caseStudy: {
        name: 'Case Study Path',
        steps: [
          { path: '/part4-case-study/', label: 'Overview' },
          { path: '/part4-case-study/chapter1-mvp/', label: 'Chapter 1: MVP' },
          { path: '/part4-case-study/chapter2-multi-city/', label: 'Chapter 2: Multi-City' }
        ]
      },
      tools: {
        name: 'Tools Path',
        steps: [
          { path: '/tools/', label: 'Overview' },
          { path: '/tools/latency-calculator/', label: 'Latency Calculator' },
          { path: '/tools/capacity-planner/', label: 'Capacity Planner' },
          { path: '/tools/consistency-visualizer/', label: 'Consistency Visualizer' },
          { path: '/tools/cap-explorer/', label: 'CAP Explorer' },
          { path: '/tools/failure-calculator/', label: 'Failure Calculator' },
          { path: '/tools/coordination-cost/', label: 'Coordination Cost' }
        ]
      }
    };
  }
  
  init() {
    // Create both traditional breadcrumbs and progress indicator
    this.createTraditionalBreadcrumbs();
    this.createProgressIndicator();
    
    // Monitor navigation changes
    this.observeNavChanges();
  }
  
  createTraditionalBreadcrumbs() {
    const existingBreadcrumbs = document.querySelector('.breadcrumbs');
    if (existingBreadcrumbs) return;
    
    const header = document.querySelector('.md-header');
    if (!header) return;
    
    const breadcrumbContainer = document.createElement('nav');
    breadcrumbContainer.className = 'breadcrumbs';
    breadcrumbContainer.setAttribute('aria-label', 'Breadcrumb navigation');
    
    const breadcrumbList = document.createElement('ol');
    breadcrumbList.className = 'breadcrumb-list';
    
    // Build breadcrumb trail
    const pathParts = this.currentPath.split('/').filter(part => part);
    let currentPath = '';
    
    // Always add home
    breadcrumbList.appendChild(this.createBreadcrumbItem('Home', '/', false));
    
    // Add path segments
    pathParts.forEach((part, index) => {
      currentPath += '/' + part;
      const isLast = index === pathParts.length - 1;
      const label = this.formatLabel(part);
      breadcrumbList.appendChild(this.createBreadcrumbItem(label, currentPath, isLast));
    });
    
    breadcrumbContainer.appendChild(breadcrumbList);
    header.after(breadcrumbContainer);
  }
  
  createBreadcrumbItem(label, path, isActive) {
    const item = document.createElement('li');
    item.className = 'breadcrumb-item';
    
    if (isActive) {
      item.setAttribute('aria-current', 'page');
      item.textContent = label;
    } else {
      const link = document.createElement('a');
      link.href = path;
      link.textContent = label;
      item.appendChild(link);
    }
    
    return item;
  }
  
  formatLabel(pathSegment) {
    // Convert path segment to readable label
    return pathSegment
      .replace(/-/g, ' ')
      .replace(/\b\w/g, char => char.toUpperCase())
      .replace(/Axiom (\d+)/, 'Axiom $1')
      .replace(/Pillar (\d+)/, 'Pillar $1')
      .replace(/Part(\d+)/, 'Part $1');
  }
  
  createProgressIndicator() {
    // Find which learning path we're on
    const currentLearningPath = this.getCurrentLearningPath();
    if (!currentLearningPath) return;
    
    const container = document.querySelector('.md-content');
    if (!container) return;
    
    const progressBar = document.createElement('div');
    progressBar.className = 'learning-progress-bar';
    progressBar.innerHTML = `
      <div class="progress-header">
        <h4>${currentLearningPath.path.name}</h4>
        <span class="progress-text">${currentLearningPath.currentStep + 1} of ${currentLearningPath.path.steps.length}</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill" style="width: ${currentLearningPath.percentage}%"></div>
      </div>
      <div class="progress-steps">
        ${this.renderProgressSteps(currentLearningPath)}
      </div>
    `;
    
    // Insert at the beginning of content
    container.insertBefore(progressBar, container.firstChild);
  }
  
  getCurrentLearningPath() {
    for (const [key, path] of Object.entries(this.learningPaths)) {
      const currentStepIndex = path.steps.findIndex(step => 
        this.currentPath.includes(step.path)
      );
      
      if (currentStepIndex !== -1) {
        return {
          key,
          path,
          currentStep: currentStepIndex,
          percentage: ((currentStepIndex + 1) / path.steps.length) * 100
        };
      }
    }
    return null;
  }
  
  renderProgressSteps(learningPath) {
    return learningPath.path.steps.map((step, index) => {
      const status = index < learningPath.currentStep ? 'completed' :
                    index === learningPath.currentStep ? 'current' : 'upcoming';
      
      return `
        <a href="${step.path}" class="progress-step ${status}" title="${step.label}">
          <span class="step-number">${index + 1}</span>
          <span class="step-label">${step.label}</span>
        </a>
      `;
    }).join('');
  }
  
  observeNavChanges() {
    // Watch for navigation changes (instant navigation)
    const observer = new MutationObserver(() => {
      if (this.currentPath !== window.location.pathname) {
        this.currentPath = window.location.pathname;
        this.updateBreadcrumbs();
        this.updateProgress();
      }
    });
    
    const target = document.querySelector('body');
    if (target) {
      observer.observe(target, {
        childList: true,
        subtree: true
      });
    }
  }
  
  updateBreadcrumbs() {
    const existingBreadcrumbs = document.querySelector('.breadcrumbs');
    if (existingBreadcrumbs) {
      existingBreadcrumbs.remove();
    }
    this.createTraditionalBreadcrumbs();
  }
  
  updateProgress() {
    const existingProgress = document.querySelector('.learning-progress-bar');
    if (existingProgress) {
      existingProgress.remove();
    }
    this.createProgressIndicator();
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new BreadcrumbNavigation());
} else {
  new BreadcrumbNavigation();
}