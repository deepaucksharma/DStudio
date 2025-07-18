// Breadcrumb Progress Bar - Shows learning path progress
class BreadcrumbProgress {
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
          { path: '/tools/cap-explorer/', label: 'CAP Explorer' }
        ]
      }
    };
  }
  
  init() {
    // Determine current learning path
    const currentPathInfo = this.getCurrentPathInfo();
    if (!currentPathInfo) return;
    
    // Create and insert progress bar
    this.createProgressBar(currentPathInfo);
    
    // Update on navigation
    this.observeNavigation();
  }
  
  getCurrentPathInfo() {
    // Normalize the current path
    const normalizedPath = this.currentPath.replace(/\/$/, '');
    
    // Find which learning path we're on
    for (const [key, pathData] of Object.entries(this.learningPaths)) {
      const stepIndex = pathData.steps.findIndex(step => 
        normalizedPath.includes(step.path.replace(/\/$/, ''))
      );
      
      if (stepIndex !== -1) {
        return {
          pathKey: key,
          pathData: pathData,
          currentStep: stepIndex,
          totalSteps: pathData.steps.length,
          progress: ((stepIndex + 1) / pathData.steps.length) * 100
        };
      }
    }
    
    return null;
  }
  
  createProgressBar(pathInfo) {
    const progressBar = document.createElement('div');
    progressBar.className = 'breadcrumb-progress-container';
    
    progressBar.innerHTML = `
      <div class="breadcrumb-progress-header">
        <span class="breadcrumb-path-name">${pathInfo.pathData.name}</span>
        <span class="breadcrumb-path-progress">${pathInfo.currentStep + 1} of ${pathInfo.totalSteps}</span>
      </div>
      <div class="breadcrumb-progress-track">
        <div class="breadcrumb-progress-fill" style="width: ${pathInfo.progress}%"></div>
        ${this.createStepMarkers(pathInfo)}
      </div>
      <div class="breadcrumb-step-labels">
        ${this.createStepLabels(pathInfo)}
      </div>
    `;
    
    // Insert after header
    const header = document.querySelector('.md-header');
    if (header && header.nextSibling) {
      header.parentNode.insertBefore(progressBar, header.nextSibling);
    }
    
    // Add click handlers
    this.attachClickHandlers(progressBar, pathInfo);
  }
  
  createStepMarkers(pathInfo) {
    return pathInfo.pathData.steps.map((step, index) => {
      const isActive = index === pathInfo.currentStep;
      const isCompleted = index < pathInfo.currentStep;
      const position = ((index + 0.5) / pathInfo.totalSteps) * 100;
      
      return `
        <div class="breadcrumb-step-marker ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}"
             style="left: ${position}%"
             data-step-index="${index}"
>
          <span class="step-marker-dot"></span>
        </div>
      `;
    }).join('');
  }
  
  createStepLabels(pathInfo) {
    const currentIndex = pathInfo.currentStep;
    const steps = pathInfo.pathData.steps;
    
    // Show current, previous, and next steps on desktop
    // Show only current on mobile
    const visibleSteps = [];
    
    if (currentIndex > 0) {
      visibleSteps.push({ ...steps[currentIndex - 1], index: currentIndex - 1, class: 'prev' });
    }
    
    visibleSteps.push({ ...steps[currentIndex], index: currentIndex, class: 'current' });
    
    if (currentIndex < steps.length - 1) {
      visibleSteps.push({ ...steps[currentIndex + 1], index: currentIndex + 1, class: 'next' });
    }
    
    return visibleSteps.map(step => {
      const position = ((step.index + 0.5) / pathInfo.totalSteps) * 100;
      return `
        <div class="breadcrumb-step-label ${step.class}"
             style="left: ${position}%"
             data-step-index="${step.index}">
          <span class="step-label-text">${step.label}</span>
        </div>
      `;
    }).join('');
  }
  
  attachClickHandlers(container, pathInfo) {
    // Handle marker clicks
    container.querySelectorAll('.breadcrumb-step-marker').forEach(marker => {
      marker.addEventListener('click', (e) => {
        const stepIndex = parseInt(marker.getAttribute('data-step-index'));
        const step = pathInfo.pathData.steps[stepIndex];
        if (step) {
          window.location.href = step.path;
        }
      });
      
      // Keyboard navigation
      marker.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          marker.click();
        }
      });
    });
    
    // Handle label clicks
    container.querySelectorAll('.breadcrumb-step-label').forEach(label => {
      label.addEventListener('click', (e) => {
        const stepIndex = parseInt(label.getAttribute('data-step-index'));
        const step = pathInfo.pathData.steps[stepIndex];
        if (step) {
          window.location.href = step.path;
        }
      });
    });
  }
  
  observeNavigation() {
    // Re-initialize on navigation changes (for instant navigation)
    if (window.navigation) {
      window.navigation.addEventListener('navigate', () => {
        setTimeout(() => {
          this.currentPath = window.location.pathname;
          this.cleanup();
          this.init();
        }, 100);
      });
    }
  }
  
  cleanup() {
    const existingProgress = document.querySelector('.breadcrumb-progress-container');
    if (existingProgress) {
      existingProgress.remove();
    }
  }
}

// Add styles dynamically
const styles = `
<style>
.breadcrumb-progress-container {
  position: sticky;
  top: 56px;
  z-index: 100;
  background: var(--md-default-bg-color);
  border-bottom: 1px solid var(--md-default-fg-color--lightest);
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.breadcrumb-progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.breadcrumb-path-name {
  font-weight: 600;
  color: var(--md-primary-fg-color);
  font-size: 0.875rem;
}

.breadcrumb-path-progress {
  color: var(--md-default-fg-color--light);
  font-size: 0.75rem;
}

.breadcrumb-progress-track {
  position: relative;
  height: 4px;
  background: var(--md-default-fg-color--lightest);
  border-radius: 2px;
  overflow: visible;
}

.breadcrumb-progress-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: linear-gradient(90deg, var(--md-primary-fg-color) 0%, var(--md-accent-fg-color) 100%);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.breadcrumb-step-marker {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  cursor: pointer;
  padding: 0.5rem;
}

.step-marker-dot {
  display: block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--md-default-bg-color);
  border: 2px solid var(--md-default-fg-color--lighter);
  transition: all 0.2s ease;
}

.breadcrumb-step-marker.completed .step-marker-dot {
  background: var(--md-primary-fg-color);
  border-color: var(--md-primary-fg-color);
}

.breadcrumb-step-marker.active .step-marker-dot {
  width: 16px;
  height: 16px;
  background: var(--md-accent-fg-color);
  border-color: var(--md-accent-fg-color);
  box-shadow: 0 0 0 4px rgba(var(--md-accent-fg-color-rgb), 0.2);
}

.breadcrumb-step-marker:hover .step-marker-dot {
  transform: scale(1.2);
}

.breadcrumb-step-labels {
  position: relative;
  height: 2rem;
  margin-top: 0.5rem;
}

.breadcrumb-step-label {
  position: absolute;
  transform: translateX(-50%);
  white-space: nowrap;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.breadcrumb-step-label.prev,
.breadcrumb-step-label.next {
  color: var(--md-default-fg-color--light);
}

.breadcrumb-step-label.current {
  color: var(--md-primary-fg-color);
  font-weight: 600;
}

.breadcrumb-step-label:hover {
  color: var(--md-accent-fg-color);
}

/* Mobile adjustments */
@media (max-width: 768px) {
  .breadcrumb-progress-container {
    padding: 0.75rem 1rem;
    top: 48px;
  }
  
  .breadcrumb-step-label.prev,
  .breadcrumb-step-label.next {
    display: none;
  }
  
  .breadcrumb-step-marker {
    padding: 0.25rem;
  }
  
  .step-marker-dot {
    width: 8px;
    height: 8px;
  }
  
  .breadcrumb-step-marker.active .step-marker-dot {
    width: 12px;
    height: 12px;
  }
}

/* Dark mode adjustments */
[data-md-color-scheme="slate"] .breadcrumb-progress-container {
  background: var(--md-default-bg-color);
  border-bottom-color: var(--md-default-fg-color--lightest);
}

[data-md-color-scheme="slate"] .breadcrumb-progress-track {
  background: var(--md-default-fg-color--lighter);
}

[data-md-color-scheme="slate"] .step-marker-dot {
  background: var(--md-default-bg-color);
}

/* Hide on print */
@media print {
  .breadcrumb-progress-container {
    display: none;
  }
}
</style>
`;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  // Add styles
  document.head.insertAdjacentHTML('beforeend', styles);
  
  // Initialize breadcrumb progress
  new BreadcrumbProgress();
});