// Privacy-focused analytics module

class Analytics {
  constructor() {
    this.enabled = this.checkConsent();
    this.sessionId = this.generateSessionId();
    this.queue = [];
    this.config = {
      endpoint: '/api/analytics',
      batchSize: 10,
      flushInterval: 30000, // 30 seconds
      sessionTimeout: 1800000, // 30 minutes
      trackingVersion: '1.0.0'
    };
    
    this.metadata = {
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      },
      screen: {
        width: window.screen.width,
        height: window.screen.height
      },
      devicePixelRatio: window.devicePixelRatio || 1,
      colorDepth: window.screen.colorDepth,
      language: navigator.language,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      referrer: document.referrer,
      userAgent: navigator.userAgent
    };
  }

  init(app) {
    this.app = app;
    
    if (!this.enabled) {
      console.log('Analytics disabled - no consent');
      return;
    }
    
    // Set up event listeners
    this.setupEventListeners();
    
    // Start session tracking
    this.startSession();
    
    // Set up batch processing
    this.startBatchProcessor();
    
    // Track initial page view
    this.trackPageView();
  }

  checkConsent() {
    // Check for analytics consent in localStorage
    const consent = localStorage.getItem('analytics-consent');
    return consent === 'granted';
  }

  requestConsent() {
    // Show consent banner
    const banner = document.createElement('div');
    banner.className = 'analytics-consent-banner';
    banner.innerHTML = `
      <div class="consent-content">
        <p>We use privacy-focused analytics to improve your experience. No personal data is collected.</p>
        <div class="consent-actions">
          <button class="consent-accept">Accept</button>
          <button class="consent-decline">Decline</button>
          <a href="/privacy" class="consent-learn-more">Learn more</a>
        </div>
      </div>
    `;
    
    document.body.appendChild(banner);
    
    // Handle consent choices
    banner.querySelector('.consent-accept').addEventListener('click', () => {
      this.grantConsent();
      banner.remove();
    });
    
    banner.querySelector('.consent-decline').addEventListener('click', () => {
      this.declineConsent();
      banner.remove();
    });
  }

  grantConsent() {
    localStorage.setItem('analytics-consent', 'granted');
    localStorage.setItem('analytics-consent-timestamp', Date.now());
    this.enabled = true;
    this.init(this.app);
  }

  declineConsent() {
    localStorage.setItem('analytics-consent', 'declined');
    localStorage.setItem('analytics-consent-timestamp', Date.now());
    this.enabled = false;
  }

  generateSessionId() {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  startSession() {
    this.sessionStart = Date.now();
    this.lastActivity = Date.now();
    
    // Update activity on user interaction
    ['click', 'scroll', 'keypress'].forEach(event => {
      document.addEventListener(event, () => {
        this.lastActivity = Date.now();
      }, { passive: true });
    });
    
    // Check for session timeout
    setInterval(() => {
      if (Date.now() - this.lastActivity > this.config.sessionTimeout) {
        this.endSession();
        this.startSession();
      }
    }, 60000); // Check every minute
  }

  endSession() {
    const duration = Date.now() - this.sessionStart;
    this.track('session_end', {
      duration,
      pageViews: this.pageViews || 0,
      events: this.eventCount || 0
    });
    this.flush();
  }

  setupEventListeners() {
    // Page visibility change
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.track('page_hidden');
        this.flush();
      } else {
        this.track('page_visible');
      }
    });
    
    // Error tracking
    window.addEventListener('error', (event) => {
      this.trackError({
        message: event.message,
        source: event.filename,
        line: event.lineno,
        column: event.colno
      });
    });
    
    // Performance tracking
    window.addEventListener('load', () => {
      setTimeout(() => {
        this.trackPerformance();
      }, 0);
    });
    
    // Scroll depth tracking
    this.trackScrollDepth();
    
    // Click tracking
    this.trackClicks();
    
    // Search tracking
    this.trackSearch();
  }

  trackPageView(customProps = {}) {
    if (!this.enabled) return;
    
    this.pageViews = (this.pageViews || 0) + 1;
    
    const pageData = {
      url: window.location.href,
      path: window.location.pathname,
      title: document.title,
      ...customProps
    };
    
    this.track('page_view', pageData);
  }

  trackEvent(category, action, label, value) {
    if (!this.enabled) return;
    
    this.track('custom_event', {
      category,
      action,
      label,
      value
    });
  }

  trackError(errorInfo) {
    if (!this.enabled) return;
    
    // Sanitize error info
    const sanitized = {
      message: errorInfo.message?.substring(0, 200),
      source: errorInfo.source?.replace(window.location.origin, ''),
      line: errorInfo.line,
      column: errorInfo.column,
      stack: errorInfo.error?.stack?.substring(0, 500)
    };
    
    this.track('error', sanitized);
  }

  trackPerformance() {
    if (!this.enabled || !window.performance) return;
    
    const navTiming = performance.timing;
    const paintMetrics = performance.getEntriesByType('paint');
    
    const metrics = {
      // Navigation timing
      dns: navTiming.domainLookupEnd - navTiming.domainLookupStart,
      tcp: navTiming.connectEnd - navTiming.connectStart,
      ttfb: navTiming.responseStart - navTiming.navigationStart,
      download: navTiming.responseEnd - navTiming.responseStart,
      domInteractive: navTiming.domInteractive - navTiming.navigationStart,
      domComplete: navTiming.domComplete - navTiming.navigationStart,
      loadComplete: navTiming.loadEventEnd - navTiming.navigationStart,
      
      // Paint timing
      firstPaint: paintMetrics.find(m => m.name === 'first-paint')?.startTime,
      firstContentfulPaint: paintMetrics.find(m => m.name === 'first-contentful-paint')?.startTime,
      
      // Resource timing
      resourceCount: performance.getEntriesByType('resource').length,
      
      // Memory (if available)
      memory: performance.memory ? {
        used: Math.round(performance.memory.usedJSHeapSize / 1048576),
        total: Math.round(performance.memory.totalJSHeapSize / 1048576)
      } : null
    };
    
    this.track('performance', metrics);
  }

  trackScrollDepth() {
    let maxScroll = 0;
    const thresholds = [25, 50, 75, 90, 100];
    const triggered = new Set();
    
    const checkScroll = this.app.throttle(() => {
      const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrollPercent = Math.round((window.scrollY / scrollHeight) * 100);
      
      maxScroll = Math.max(maxScroll, scrollPercent);
      
      thresholds.forEach(threshold => {
        if (scrollPercent >= threshold && !triggered.has(threshold)) {
          triggered.add(threshold);
          this.track('scroll_depth', {
            depth: threshold,
            path: window.location.pathname
          });
        }
      });
    }, 500);
    
    window.addEventListener('scroll', checkScroll, { passive: true });
    
    // Track max scroll on page leave
    window.addEventListener('beforeunload', () => {
      if (maxScroll > 0) {
        this.track('max_scroll_depth', {
          depth: maxScroll,
          path: window.location.pathname
        });
      }
    });
  }

  trackClicks() {
    document.addEventListener('click', (event) => {
      const target = event.target.closest('a, button, [data-track-click]');
      if (!target) return;
      
      const trackingData = {
        type: target.tagName.toLowerCase(),
        text: target.textContent?.substring(0, 50),
        href: target.href?.replace(window.location.origin, ''),
        classes: target.className,
        dataAttributes: Object.keys(target.dataset)
      };
      
      // Special tracking for specific elements
      if (target.classList.contains('hero-button')) {
        this.track('cta_click', { ...trackingData, cta: 'hero' });
      } else if (target.closest('.tool-container')) {
        this.track('tool_interaction', { ...trackingData, tool: target.closest('.tool-container').dataset.tool });
      } else if (target.closest('nav')) {
        this.track('navigation_click', trackingData);
      }
    });
  }

  trackSearch() {
    const searchInput = document.querySelector('.md-search__input');
    if (!searchInput) return;
    
    let searchTimer;
    searchInput.addEventListener('input', (event) => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        if (event.target.value.length > 2) {
          this.track('search', {
            query: event.target.value,
            resultsCount: document.querySelectorAll('.md-search-result__item').length
          });
        }
      }, 1000);
    });
  }

  track(eventName, data = {}) {
    if (!this.enabled) return;
    
    const event = {
      name: eventName,
      timestamp: Date.now(),
      sessionId: this.sessionId,
      data: {
        ...data,
        path: window.location.pathname,
        viewport: `${window.innerWidth}x${window.innerHeight}`
      }
    };
    
    this.queue.push(event);
    this.eventCount = (this.eventCount || 0) + 1;
    
    // Flush if queue is full
    if (this.queue.length >= this.config.batchSize) {
      this.flush();
    }
  }

  startBatchProcessor() {
    // Flush events periodically
    setInterval(() => {
      if (this.queue.length > 0) {
        this.flush();
      }
    }, this.config.flushInterval);
    
    // Flush on page unload
    window.addEventListener('beforeunload', () => {
      this.flush();
    });
  }

  async flush() {
    if (this.queue.length === 0) return;
    
    const events = [...this.queue];
    this.queue = [];
    
    try {
      // In production, this would send to your analytics endpoint
      if (this.config.endpoint.startsWith('/api/')) {
        console.log('Analytics batch:', events);
        // await fetch(this.config.endpoint, {
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify({ events, metadata: this.metadata })
        // });
      }
    } catch (error) {
      console.error('Failed to send analytics:', error);
      // Re-queue events on failure
      this.queue.unshift(...events);
    }
  }

  // Public API for custom tracking
  page(name, properties) {
    this.trackPageView(properties);
  }

  event(name, properties) {
    this.track(name, properties);
  }

  identify(userId, traits) {
    // Store user traits for future events
    this.userId = userId;
    this.userTraits = traits;
  }
}

// Register with app
if (window.DSApp) {
  window.DSApp.register('analytics', new Analytics());
}

export default Analytics;