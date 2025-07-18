// Enhanced Tool UX Components

// Add reset and copy functionality to all tools
document.addEventListener('DOMContentLoaded', () => {
  enhanceToolContainers();
});

function enhanceToolContainers() {
  const tools = document.querySelectorAll('.interactive-tool, .tool-container');
  
  tools.forEach(tool => {
    // Check if tool already has action buttons
    if (tool.querySelector('.tool-actions')) return;
    
    // Create action buttons container
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'tool-actions';
    
    // Reset button
    const resetBtn = document.createElement('button');
    resetBtn.className = 'tool-button secondary';
    resetBtn.innerHTML = '↻ Reset';
    resetBtn.addEventListener('click', () => resetToolInputs(tool));
    
    // Copy results button
    const copyBtn = document.createElement('button');
    copyBtn.className = 'tool-button secondary';
    copyBtn.innerHTML = '📋 Copy Results';
    copyBtn.addEventListener('click', () => copyToolResults(tool));
    
    actionsDiv.appendChild(resetBtn);
    actionsDiv.appendChild(copyBtn);
    
    // Find form or inputs container
    const form = tool.querySelector('form');
    const inputsContainer = tool.querySelector('.tool-inputs') || form;
    
    if (inputsContainer) {
      inputsContainer.appendChild(actionsDiv);
    }
    
    // Add input hints
    enhanceInputLabels(tool);
    
    // Make results sticky on desktop
    makeResultsSticky(tool);
  });
}

function resetToolInputs(toolContainer) {
  const form = toolContainer.querySelector('form');
  if (form) {
    form.reset();
    
    // Trigger change event to update results
    const event = new Event('change', { bubbles: true });
    form.dispatchEvent(event);
  }
  
  // Reset any custom elements
  const customResets = toolContainer.querySelectorAll('[data-default]');
  customResets.forEach(element => {
    if (element.value !== undefined) {
      element.value = element.dataset.default;
    }
  });
  
  // Show confirmation
  showToast('Tool reset to defaults');
}

function copyToolResults(toolContainer) {
  const results = toolContainer.querySelector('.tool-results, .results-panel, #results');
  if (!results) {
    showToast('No results to copy');
    return;
  }
  
  // Extract text content
  let textContent = '';
  const resultItems = results.querySelectorAll('.result-item, .result-row');
  
  resultItems.forEach(item => {
    const label = item.querySelector('.result-label, .label')?.textContent || '';
    const value = item.querySelector('.result-value, .value')?.textContent || '';
    if (label && value) {
      textContent += `${label}: ${value}\n`;
    }
  });
  
  // If no structured results, copy all text
  if (!textContent) {
    textContent = results.textContent.trim();
  }
  
  // Copy to clipboard
  navigator.clipboard.writeText(textContent).then(() => {
    showToast('Results copied to clipboard');
  }).catch(() => {
    showToast('Failed to copy results');
  });
}

function enhanceInputLabels(toolContainer) {
  const inputs = toolContainer.querySelectorAll('input[type="number"], input[type="text"], select');
  
  inputs.forEach(input => {
    // Add units or hints based on common patterns
    const label = input.previousElementSibling || input.parentElement.querySelector('label');
    if (!label) return;
    
    const labelText = label.textContent.toLowerCase();
    let hint = '';
    
    // Add contextual hints
    if (labelText.includes('distance')) {
      hint = 'in kilometers';
    } else if (labelText.includes('time') || labelText.includes('delay')) {
      hint = 'in milliseconds';
    } else if (labelText.includes('size')) {
      hint = 'in bytes';
    } else if (labelText.includes('rate')) {
      hint = 'per second';
    } else if (labelText.includes('bandwidth')) {
      hint = 'in Mbps';
    } else if (labelText.includes('percentage') || labelText.includes('%')) {
      hint = '0-100';
    }
    
    if (hint && !label.querySelector('.input-hint')) {
      const hintSpan = document.createElement('span');
      hintSpan.className = 'input-hint';
      hintSpan.textContent = ` (${hint})`;
      label.appendChild(hintSpan);
    }
    
    // Add placeholder if missing
    if (!input.placeholder && hint) {
      input.placeholder = hint;
    }
  });
}

function makeResultsSticky(toolContainer) {
  // Only on desktop
  if (window.innerWidth <= 768) return;
  
  const results = toolContainer.querySelector('.tool-results, .results-panel');
  const inputs = toolContainer.querySelector('.tool-inputs, form');
  
  if (results && inputs && !toolContainer.classList.contains('tool-container')) {
    // Wrap in container
    const wrapper = document.createElement('div');
    wrapper.className = 'tool-container';
    
    toolContainer.appendChild(wrapper);
    wrapper.appendChild(inputs);
    wrapper.appendChild(results);
    
    // Mark results as sticky
    results.classList.add('sticky-results');
  }
}

// Toast notification system
function showToast(message, duration = 3000) {
  // Remove existing toast
  const existingToast = document.querySelector('.tool-toast');
  if (existingToast) {
    existingToast.remove();
  }
  
  const toast = document.createElement('div');
  toast.className = 'tool-toast';
  toast.textContent = message;
  
  document.body.appendChild(toast);
  
  // Trigger animation
  setTimeout(() => toast.classList.add('show'), 10);
  
  // Remove after duration
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// Enhanced form validation
function addFormValidation(form) {
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const inputs = form.querySelectorAll('input[required], select[required]');
    let valid = true;
    
    inputs.forEach(input => {
      if (!input.value) {
        input.classList.add('error');
        valid = false;
      } else {
        input.classList.remove('error');
      }
    });
    
    if (!valid) {
      showToast('Please fill in all required fields');
    }
  });
  
  // Clear error on input
  form.addEventListener('input', (e) => {
    if (e.target.classList.contains('error')) {
      e.target.classList.remove('error');
    }
  });
}

// Keyboard shortcuts for tools
document.addEventListener('keydown', (e) => {
  // Ctrl/Cmd + Shift + R = Reset tool
  if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'R') {
    const activeToolForm = document.querySelector('.interactive-tool form, .tool-container form');
    if (activeToolForm) {
      e.preventDefault();
      resetToolInputs(activeToolForm.closest('.interactive-tool, .tool-container'));
    }
  }
  
  // Ctrl/Cmd + Shift + C = Copy results
  if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
    const activeToolResults = document.querySelector('.interactive-tool .tool-results, .tool-container .tool-results');
    if (activeToolResults) {
      e.preventDefault();
      copyToolResults(activeToolResults.closest('.interactive-tool, .tool-container'));
    }
  }
});

// Add CSS for toast notifications
const toastStyles = `
<style>
.tool-toast {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%) translateY(100px);
  background-color: var(--md-default-fg-color);
  color: var(--md-default-bg-color);
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  z-index: 1000;
  opacity: 0;
  transition: all 0.3s ease;
}

.tool-toast.show {
  transform: translateX(-50%) translateY(0);
  opacity: 1;
}

input.error {
  border-color: #ef5350 !important;
}

.sticky-results {
  position: sticky;
  top: 5rem;
  max-height: calc(100vh - 6rem);
  overflow-y: auto;
}

/* Tool action buttons hover effects */
.tool-button:active {
  transform: scale(0.95);
}

/* Input hints styling */
.input-hint {
  font-size: 0.75rem;
  color: var(--md-default-fg-color--light);
  font-weight: normal;
}

/* Mobile adjustments */
@media (max-width: 768px) {
  .tool-container {
    display: block;
  }
  
  .sticky-results {
    position: relative;
    top: 0;
  }
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', toastStyles);