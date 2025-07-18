// Security module for content protection and XSS prevention

class Security {
  constructor() {
    this.cspNonce = this.generateNonce();
    this.trustedTypes = this.setupTrustedTypes();
  }

  init(app) {
    this.app = app;
    
    // Set up Content Security Policy
    this.setupCSP();
    
    // Set up XSS protection
    this.setupXSSProtection();
    
    // Set up CSRF protection
    this.setupCSRFProtection();
    
    // Monitor security violations
    this.monitorViolations();
    
    // Set up input sanitization
    this.setupInputSanitization();
  }

  generateNonce() {
    const array = new Uint8Array(16);
    crypto.getRandomValues(array);
    return btoa(String.fromCharCode.apply(null, array));
  }

  setupCSP() {
    // Create CSP meta tag
    const cspMeta = document.createElement('meta');
    cspMeta.httpEquiv = 'Content-Security-Policy';
    cspMeta.content = `
      default-src 'self';
      script-src 'self' 'nonce-${this.cspNonce}' https://cdn.jsdelivr.net;
      style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
      font-src 'self' https://fonts.gstatic.com;
      img-src 'self' data: https:;
      connect-src 'self' https://api.github.com;
      frame-ancestors 'none';
      base-uri 'self';
      form-action 'self';
      upgrade-insecure-requests;
    `.replace(/\s+/g, ' ').trim();
    
    document.head.appendChild(cspMeta);
  }

  setupTrustedTypes() {
    if (!window.trustedTypes) return null;
    
    try {
      const policy = trustedTypes.createPolicy('default', {
        createHTML: (input) => this.sanitizeHTML(input),
        createScript: (input) => {
          throw new Error('Dynamic script creation not allowed');
        },
        createScriptURL: (input) => {
          const allowed = [
            'https://cdn.jsdelivr.net/',
            window.location.origin
          ];
          
          if (allowed.some(origin => input.startsWith(origin))) {
            return input;
          }
          throw new Error('Script URL not allowed: ' + input);
        }
      });
      
      return policy;
    } catch (error) {
      console.error('Trusted Types setup failed:', error);
      return null;
    }
  }

  setupXSSProtection() {
    // Override dangerous methods
    const dangerous = ['innerHTML', 'outerHTML', 'insertAdjacentHTML'];
    
    dangerous.forEach(method => {
      const original = Element.prototype[method];
      
      Object.defineProperty(Element.prototype, method, {
        set: function(value) {
          if (method === 'innerHTML' || method === 'outerHTML') {
            // Sanitize before setting
            const sanitized = this.security?.sanitizeHTML(value) || value;
            original.call(this, sanitized);
          } else if (method === 'insertAdjacentHTML') {
            // Wrap the original method
            return function(position, html) {
              const sanitized = this.security?.sanitizeHTML(html) || html;
              return original.call(this, position, sanitized);
            };
          }
        }
      });
    });
    
    // Protect against prototype pollution
    Object.freeze(Object.prototype);
    Object.freeze(Array.prototype);
  }

  sanitizeHTML(input) {
    // Create a temporary element to parse HTML
    const temp = document.createElement('div');
    temp.textContent = input; // This escapes HTML
    
    // Allow specific safe tags and attributes
    const allowedTags = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li', 'code', 'pre'];
    const allowedAttributes = {
      'a': ['href', 'title'],
      'code': ['class']
    };
    
    // Parse and filter
    const fragment = document.createDocumentFragment();
    const parser = new DOMParser();
    const doc = parser.parseFromString(input, 'text/html');
    
    const sanitize = (node) => {
      if (node.nodeType === Node.TEXT_NODE) {
        return node.cloneNode(true);
      }
      
      if (node.nodeType === Node.ELEMENT_NODE) {
        const tagName = node.tagName.toLowerCase();
        
        if (!allowedTags.includes(tagName)) {
          // Skip disallowed tags but process children
          const frag = document.createDocumentFragment();
          Array.from(node.childNodes).forEach(child => {
            const sanitized = sanitize(child);
            if (sanitized) frag.appendChild(sanitized);
          });
          return frag;
        }
        
        // Create clean element
        const clean = document.createElement(tagName);
        
        // Copy allowed attributes
        const allowed = allowedAttributes[tagName] || [];
        allowed.forEach(attr => {
          if (node.hasAttribute(attr)) {
            let value = node.getAttribute(attr);
            
            // Special handling for href
            if (attr === 'href') {
              if (!value.startsWith('http://') && 
                  !value.startsWith('https://') && 
                  !value.startsWith('/') && 
                  !value.startsWith('#')) {
                return; // Skip suspicious URLs
              }
            }
            
            clean.setAttribute(attr, value);
          }
        });
        
        // Process children
        Array.from(node.childNodes).forEach(child => {
          const sanitized = sanitize(child);
          if (sanitized) clean.appendChild(sanitized);
        });
        
        return clean;
      }
      
      return null;
    };
    
    Array.from(doc.body.childNodes).forEach(node => {
      const sanitized = sanitize(node);
      if (sanitized) fragment.appendChild(sanitized);
    });
    
    // Convert back to string
    const container = document.createElement('div');
    container.appendChild(fragment);
    return container.innerHTML;
  }

  setupCSRFProtection() {
    // Generate CSRF token
    this.csrfToken = this.generateToken();
    
    // Add to all forms
    document.addEventListener('submit', (event) => {
      const form = event.target;
      if (form.method.toLowerCase() === 'post') {
        // Add CSRF token
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'csrf_token';
        input.value = this.csrfToken;
        form.appendChild(input);
      }
    });
    
    // Add to fetch requests
    const originalFetch = window.fetch;
    window.fetch = (url, options = {}) => {
      if (options.method && options.method.toUpperCase() !== 'GET') {
        // Add CSRF header
        options.headers = {
          ...options.headers,
          'X-CSRF-Token': this.csrfToken
        };
      }
      return originalFetch(url, options);
    };
  }

  generateToken() {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }

  monitorViolations() {
    // CSP violation reporting
    document.addEventListener('securitypolicyviolation', (event) => {
      const violation = {
        documentURI: event.documentURI,
        violatedDirective: event.violatedDirective,
        effectiveDirective: event.effectiveDirective,
        originalPolicy: event.originalPolicy,
        blockedURI: event.blockedURI,
        lineNumber: event.lineNumber,
        columnNumber: event.columnNumber,
        sourceFile: event.sourceFile,
        timestamp: Date.now()
      };
      
      console.error('CSP Violation:', violation);
      
      // Report to analytics
      this.app.emit('security:violation', violation);
    });
  }

  setupInputSanitization() {
    // Auto-sanitize form inputs
    document.addEventListener('input', (event) => {
      const input = event.target;
      
      if (input.tagName === 'INPUT' || input.tagName === 'TEXTAREA') {
        // Remove any script tags or dangerous content
        const dangerous = /<script|javascript:|on\w+=/gi;
        
        if (dangerous.test(input.value)) {
          input.value = input.value.replace(dangerous, '');
          
          // Show warning
          this.showSecurityWarning('Potentially dangerous content removed');
        }
      }
    });
  }

  showSecurityWarning(message) {
    const warning = document.createElement('div');
    warning.className = 'security-warning';
    warning.textContent = message;
    
    document.body.appendChild(warning);
    
    setTimeout(() => {
      warning.classList.add('show');
    }, 10);
    
    setTimeout(() => {
      warning.classList.remove('show');
      setTimeout(() => warning.remove(), 300);
    }, 3000);
  }

  // Public API
  escape(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  validateURL(url) {
    try {
      const parsed = new URL(url);
      // Only allow http(s) and relative URLs
      return parsed.protocol === 'http:' || 
             parsed.protocol === 'https:' || 
             url.startsWith('/');
    } catch {
      return false;
    }
  }

  validateEmail(email) {
    // Basic email validation
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }
}

// Register with app
if (window.DSApp) {
  window.DSApp.register('security', new Security());
}

// Add security styles
const securityStyles = `
<style>
.security-warning {
  position: fixed;
  top: 20px;
  right: 20px;
  background: #f44336;
  color: white;
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 14px;
  opacity: 0;
  transform: translateX(100%);
  transition: all 0.3s ease;
  z-index: 10000;
}

.security-warning.show {
  opacity: 1;
  transform: translateX(0);
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', securityStyles);

export default Security;