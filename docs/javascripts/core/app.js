// Core Application Module - Centralized initialization and coordination

class DistributedSystemsApp {
  constructor() {
    this.modules = new Map();
    this.config = this.loadConfig();
    this.state = {
      initialized: false,
      theme: 'auto',
      preferences: {},
      performance: {
        loadTime: performance.now(),
        interactions: 0
      }
    };
  }

  // Module registration system
  register(name, module) {
    if (this.modules.has(name)) {
      console.warn(`Module ${name} already registered`);
      return;
    }
    this.modules.set(name, module);
  }

  // Initialize all modules in correct order
  async init() {
    try {
      // Load user preferences
      await this.loadUserPreferences();
      
      // Initialize core modules first
      await this.initCoreModules();
      
      // Initialize UI components
      await this.initUIComponents();
      
      // Initialize tools last
      await this.initTools();
      
      // Set up global error handling
      this.setupErrorHandling();
      
      // Mark as initialized
      this.state.initialized = true;
      
      // Emit ready event
      window.dispatchEvent(new CustomEvent('app:ready', { 
        detail: { modules: Array.from(this.modules.keys()) } 
      }));
      
      // Log performance metrics
      this.logPerformance();
      
    } catch (error) {
      console.error('App initialization failed:', error);
      this.handleCriticalError(error);
    }
  }

  async initCoreModules() {
    const coreModules = [
      'performance',
      'navigation',
      'mobile',
      'analytics',
      'preferences',
      'offline'
    ];
    
    for (const moduleName of coreModules) {
      const module = this.modules.get(moduleName);
      if (module && module.init) {
        try {
          await module.init(this);
        } catch (error) {
          console.error(`Failed to initialize ${moduleName}:`, error);
        }
      }
    }
  }

  async initUIComponents() {
    const uiModules = [
      'hero',
      'journey-map',
      'tooltips',
      'reading-progress',
      'breadcrumbs',
      'toc',
      'search'
    ];
    
    // Initialize in parallel where possible
    const promises = uiModules.map(moduleName => {
      const module = this.modules.get(moduleName);
      if (module && module.init) {
        return module.init(this).catch(error => {
          console.error(`Failed to initialize ${moduleName}:`, error);
        });
      }
    });
    
    await Promise.all(promises);
  }

  async initTools() {
    // Tools are initialized on-demand for performance
    const toolsContainer = document.querySelector('.interactive-tool, .tool-container');
    if (toolsContainer) {
      const toolName = toolsContainer.dataset.tool;
      if (toolName) {
        const module = this.modules.get(`tool:${toolName}`);
        if (module && module.init) {
          await module.init(this);
        }
      }
    }
  }

  loadConfig() {
    return {
      api: {
        baseUrl: window.location.origin,
        timeout: 10000
      },
      features: {
        offline: true,
        analytics: true,
        animations: !window.matchMedia('(prefers-reduced-motion: reduce)').matches,
        darkMode: window.matchMedia('(prefers-color-scheme: dark)').matches
      },
      performance: {
        lazyLoadOffset: 50,
        debounceDelay: 150,
        cacheExpiry: 3600000 // 1 hour
      }
    };
  }

  async loadUserPreferences() {
    try {
      const stored = localStorage.getItem('ds-preferences');
      if (stored) {
        this.state.preferences = JSON.parse(stored);
      }
    } catch (error) {
      console.warn('Failed to load preferences:', error);
    }
  }

  savePreference(key, value) {
    this.state.preferences[key] = value;
    try {
      localStorage.setItem('ds-preferences', JSON.stringify(this.state.preferences));
    } catch (error) {
      console.warn('Failed to save preference:', error);
    }
  }

  getPreference(key, defaultValue = null) {
    return this.state.preferences[key] ?? defaultValue;
  }

  // Global event bus
  emit(eventName, data) {
    window.dispatchEvent(new CustomEvent(`app:${eventName}`, { detail: data }));
  }

  on(eventName, handler) {
    window.addEventListener(`app:${eventName}`, handler);
  }

  off(eventName, handler) {
    window.removeEventListener(`app:${eventName}`, handler);
  }

  // Performance monitoring
  logPerformance() {
    const loadTime = performance.now() - this.state.performance.loadTime;
    const metrics = {
      loadTime,
      domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
      resourceCount: performance.getEntriesByType('resource').length,
      memoryUsage: performance.memory ? {
        used: Math.round(performance.memory.usedJSHeapSize / 1048576),
        total: Math.round(performance.memory.totalJSHeapSize / 1048576)
      } : null
    };
    
    console.log('Performance metrics:', metrics);
    this.emit('performance:measured', metrics);
  }

  // Error handling
  setupErrorHandling() {
    window.addEventListener('error', (event) => {
      this.handleError({
        message: event.message,
        source: event.filename,
        line: event.lineno,
        column: event.colno,
        error: event.error
      });
    });

    window.addEventListener('unhandledrejection', (event) => {
      this.handleError({
        message: 'Unhandled promise rejection',
        error: event.reason
      });
    });
  }

  handleError(errorInfo) {
    console.error('Application error:', errorInfo);
    
    // Send to analytics if available
    const analytics = this.modules.get('analytics');
    if (analytics && analytics.trackError) {
      analytics.trackError(errorInfo);
    }
    
    // Show user-friendly error message for critical errors
    if (errorInfo.critical) {
      this.showErrorMessage('Something went wrong. Please refresh the page.');
    }
  }

  handleCriticalError(error) {
    this.handleError({ ...error, critical: true });
  }

  showErrorMessage(message) {
    const toast = document.createElement('div');
    toast.className = 'error-toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.classList.add('show');
    }, 10);
    
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, 5000);
  }

  // Utility methods
  debounce(func, delay) {
    let timeoutId;
    return (...args) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
  }

  throttle(func, limit) {
    let inThrottle;
    return (...args) => {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }

  // Lazy loading helper
  lazyLoad(selector, callback) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          callback(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, {
      rootMargin: `${this.config.performance.lazyLoadOffset}px`
    });

    document.querySelectorAll(selector).forEach(el => {
      observer.observe(el);
    });
  }
}

// Create global app instance
window.DSApp = new DistributedSystemsApp();

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => window.DSApp.init());
} else {
  window.DSApp.init();
}