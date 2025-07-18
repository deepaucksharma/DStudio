// User Preferences Management System

(function() {
  'use strict';

  class PreferencesManager {
    constructor() {
      this.preferences = this.loadPreferences();
      this.defaults = {
        theme: 'auto',
        fontSize: 'medium',
        codeTheme: 'material',
        animations: true,
        reduceMotion: false,
        autoplayVideos: false,
        expandSidebar: true,
        showLineNumbers: true,
        enableShortcuts: true,
        readingProgress: true,
        smoothScroll: true,
        language: 'en',
        density: 'comfortable',
        tooltips: true,
        soundEffects: false
      };
    }

    init(app) {
      this.app = app;
      
      // Apply saved preferences
      this.applyAllPreferences();
      
      // Create preferences UI
      this.createPreferencesPanel();
      
      // Listen for system preference changes
      this.watchSystemPreferences();
      
      // Set up keyboard shortcuts
      this.setupKeyboardShortcuts();
    }

    loadPreferences() {
      try {
        const saved = localStorage.getItem('ds-preferences');
        return saved ? JSON.parse(saved) : {};
      } catch (error) {
        console.error('Failed to load preferences:', error);
        return {};
      }
    }

    savePreferences() {
      try {
        localStorage.setItem('ds-preferences', JSON.stringify(this.preferences));
        this.app.emit('preferences:saved', this.preferences);
      } catch (error) {
        console.error('Failed to save preferences:', error);
      }
    }

    get(key, defaultValue = null) {
      return this.preferences[key] ?? this.defaults[key] ?? defaultValue;
    }

    set(key, value) {
      this.preferences[key] = value;
      this.savePreferences();
      this.applyPreference(key, value);
      this.app.emit('preference:changed', { key, value });
    }

    reset(key = null) {
      if (key) {
        delete this.preferences[key];
        this.applyPreference(key, this.defaults[key]);
      } else {
        this.preferences = {};
        this.applyAllPreferences();
      }
      this.savePreferences();
    }

    applyAllPreferences() {
      Object.keys(this.defaults).forEach(key => {
        this.applyPreference(key, this.get(key));
      });
    }

    applyPreference(key, value) {
      switch (key) {
        case 'theme':
          this.applyTheme(value);
          break;
        case 'fontSize':
          this.applyFontSize(value);
          break;
        case 'codeTheme':
          this.applyCodeTheme(value);
          break;
        case 'animations':
          this.toggleAnimations(value);
          break;
        case 'reduceMotion':
          this.setReducedMotion(value);
          break;
        case 'expandSidebar':
          this.setSidebarExpanded(value);
          break;
        case 'showLineNumbers':
          this.toggleLineNumbers(value);
          break;
        case 'readingProgress':
          this.toggleReadingProgress(value);
          break;
        case 'smoothScroll':
          this.toggleSmoothScroll(value);
          break;
        case 'density':
          this.setDensity(value);
          break;
        case 'tooltips':
          this.toggleTooltips(value);
          break;
      }
    }

    applyTheme(theme) {
      const root = document.documentElement;
      
      if (theme === 'auto') {
        // Use system preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        theme = prefersDark ? 'dark' : 'light';
      }
      
      root.setAttribute('data-theme', theme);
      
      // Update Material theme toggle
      const themeToggle = document.querySelector('[data-md-component="palette"]');
      if (themeToggle) {
        const isDark = theme === 'dark';
        themeToggle.querySelector('input').checked = isDark;
      }
    }

    applyFontSize(size) {
      const root = document.documentElement;
      const sizes = {
        small: '14px',
        medium: '16px',
        large: '18px',
        xlarge: '20px'
      };
      
      root.style.setProperty('--md-text-font-size', sizes[size] || sizes.medium);
      root.setAttribute('data-font-size', size);
    }

    applyCodeTheme(theme) {
      const themes = {
        material: 'material',
        monokai: 'monokai',
        github: 'github',
        dracula: 'dracula',
        solarized: 'solarized-light'
      };
      
      document.documentElement.setAttribute('data-code-theme', themes[theme] || 'material');
    }

    toggleAnimations(enabled) {
      document.documentElement.classList.toggle('no-animations', !enabled);
    }

    setReducedMotion(reduced) {
      document.documentElement.classList.toggle('reduce-motion', reduced);
      
      if (reduced) {
        // Disable all animations
        this.set('animations', false);
        this.set('smoothScroll', false);
      }
    }

    setSidebarExpanded(expanded) {
      const sidebar = document.querySelector('[data-md-component="sidebar"]');
      if (sidebar) {
        sidebar.classList.toggle('md-sidebar--expanded', expanded);
      }
    }

    toggleLineNumbers(show) {
      document.documentElement.classList.toggle('hide-line-numbers', !show);
    }

    toggleReadingProgress(show) {
      const progress = document.querySelector('.reading-progress-container');
      if (progress) {
        progress.style.display = show ? 'block' : 'none';
      }
    }

    toggleSmoothScroll(enabled) {
      document.documentElement.style.scrollBehavior = enabled ? 'smooth' : 'auto';
    }

    setDensity(density) {
      const densities = {
        compact: '0.5rem',
        comfortable: '1rem',
        spacious: '1.5rem'
      };
      
      document.documentElement.style.setProperty('--content-padding', densities[density]);
      document.documentElement.setAttribute('data-density', density);
    }

    toggleTooltips(enabled) {
      document.documentElement.classList.toggle('hide-tooltips', !enabled);
    }

    watchSystemPreferences() {
      // Watch for system theme changes
      const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
      darkModeQuery.addEventListener('change', (e) => {
        if (this.get('theme') === 'auto') {
          this.applyTheme('auto');
        }
      });
      
      // Watch for reduced motion preference
      const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
      reducedMotionQuery.addEventListener('change', (e) => {
        if (e.matches && !this.get('reduceMotion')) {
          this.set('reduceMotion', true);
        }
      });
    }

    createPreferencesPanel() {
      const panel = document.createElement('div');
      panel.className = 'preferences-panel';
      panel.innerHTML = `
        <div class="preferences-header">
          <h3>Preferences</h3>
          <button class="preferences-close" aria-label="Close preferences">×</button>
        </div>
        <div class="preferences-content">
          ${this.createPreferenceGroups()}
        </div>
        <div class="preferences-footer">
          <button class="btn-reset-all">Reset All</button>
          <button class="btn-export">Export</button>
          <button class="btn-import">Import</button>
        </div>
      `;
      
      document.body.appendChild(panel);
      
      // Add trigger button
      const trigger = document.createElement('button');
      trigger.className = 'preferences-trigger';
      trigger.innerHTML = '⚙️';
      trigger.title = 'Open preferences';
      document.body.appendChild(trigger);
      
      // Event listeners
      this.setupPanelListeners(panel, trigger);
    }

    createPreferenceGroups() {
      return `
        <div class="preference-group">
          <h4>Appearance</h4>
          ${this.createPreferenceControl('theme', 'Theme', 'select', [
            { value: 'auto', label: 'Auto' },
            { value: 'light', label: 'Light' },
            { value: 'dark', label: 'Dark' }
          ])}
          ${this.createPreferenceControl('fontSize', 'Font Size', 'select', [
            { value: 'small', label: 'Small' },
            { value: 'medium', label: 'Medium' },
            { value: 'large', label: 'Large' },
            { value: 'xlarge', label: 'Extra Large' }
          ])}
          ${this.createPreferenceControl('codeTheme', 'Code Theme', 'select', [
            { value: 'material', label: 'Material' },
            { value: 'monokai', label: 'Monokai' },
            { value: 'github', label: 'GitHub' },
            { value: 'dracula', label: 'Dracula' },
            { value: 'solarized', label: 'Solarized' }
          ])}
          ${this.createPreferenceControl('density', 'Content Density', 'select', [
            { value: 'compact', label: 'Compact' },
            { value: 'comfortable', label: 'Comfortable' },
            { value: 'spacious', label: 'Spacious' }
          ])}
        </div>
        
        <div class="preference-group">
          <h4>Behavior</h4>
          ${this.createPreferenceControl('animations', 'Enable Animations', 'toggle')}
          ${this.createPreferenceControl('smoothScroll', 'Smooth Scrolling', 'toggle')}
          ${this.createPreferenceControl('tooltips', 'Show Tooltips', 'toggle')}
          ${this.createPreferenceControl('autoplayVideos', 'Autoplay Videos', 'toggle')}
          ${this.createPreferenceControl('soundEffects', 'Sound Effects', 'toggle')}
        </div>
        
        <div class="preference-group">
          <h4>Reading</h4>
          ${this.createPreferenceControl('readingProgress', 'Show Reading Progress', 'toggle')}
          ${this.createPreferenceControl('showLineNumbers', 'Show Line Numbers', 'toggle')}
          ${this.createPreferenceControl('expandSidebar', 'Expand Sidebar by Default', 'toggle')}
          ${this.createPreferenceControl('enableShortcuts', 'Enable Keyboard Shortcuts', 'toggle')}
        </div>
        
        <div class="preference-group">
          <h4>Accessibility</h4>
          ${this.createPreferenceControl('reduceMotion', 'Reduce Motion', 'toggle')}
        </div>
      `;
    }

    createPreferenceControl(key, label, type, options = null) {
      const value = this.get(key);
      const id = `pref-${key}`;
      
      if (type === 'toggle') {
        return `
          <div class="preference-control">
            <label for="${id}">${label}</label>
            <input type="checkbox" id="${id}" data-pref="${key}" 
                   ${value ? 'checked' : ''} class="toggle-switch">
          </div>
        `;
      } else if (type === 'select' && options) {
        return `
          <div class="preference-control">
            <label for="${id}">${label}</label>
            <select id="${id}" data-pref="${key}">
              ${options.map(opt => `
                <option value="${opt.value}" ${value === opt.value ? 'selected' : ''}>
                  ${opt.label}
                </option>
              `).join('')}
            </select>
          </div>
        `;
      }
    }

    setupPanelListeners(panel, trigger) {
      // Open/close panel
      trigger.addEventListener('click', () => {
        panel.classList.add('show');
      });
      
      panel.querySelector('.preferences-close').addEventListener('click', () => {
        panel.classList.remove('show');
      });
      
      // Handle preference changes
      panel.addEventListener('change', (e) => {
        const pref = e.target.dataset.pref;
        if (pref) {
          const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
          this.set(pref, value);
        }
      });
      
      // Reset all
      panel.querySelector('.btn-reset-all').addEventListener('click', () => {
        if (confirm('Reset all preferences to defaults?')) {
          this.reset();
          location.reload();
        }
      });
      
      // Export preferences
      panel.querySelector('.btn-export').addEventListener('click', () => {
        const data = JSON.stringify(this.preferences, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'ds-preferences.json';
        a.click();
        URL.revokeObjectURL(url);
      });
      
      // Import preferences
      panel.querySelector('.btn-import').addEventListener('click', () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.addEventListener('change', (e) => {
          const file = e.target.files[0];
          if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
              try {
                const imported = JSON.parse(e.target.result);
                this.preferences = { ...this.preferences, ...imported };
                this.savePreferences();
                this.applyAllPreferences();
                location.reload();
              } catch (error) {
                alert('Invalid preferences file');
              }
            };
            reader.readAsText(file);
          }
        });
        input.click();
      });
    }

    setupKeyboardShortcuts() {
      if (!this.get('enableShortcuts')) return;
      
      document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + ,
        if ((e.ctrlKey || e.metaKey) && e.key === ',') {
          e.preventDefault();
          document.querySelector('.preferences-trigger').click();
        }
        
        // Ctrl/Cmd + Shift + T - Toggle theme
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
          e.preventDefault();
          const current = this.get('theme');
          const next = current === 'light' ? 'dark' : 'light';
          this.set('theme', next);
        }
      });
    }
  }

  // Register with app
  if (window.DSApp) {
    window.DSApp.register('preferences', new PreferencesManager());
  }

  // Add styles
  const styles = `
    <style>
    .preferences-trigger {
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: var(--md-primary-fg-color);
      color: white;
      border: none;
      font-size: 20px;
      cursor: pointer;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
      z-index: 100;
      transition: transform 0.2s;
    }
    
    .preferences-trigger:hover {
      transform: scale(1.1);
    }
    
    .preferences-panel {
      position: fixed;
      right: 0;
      top: 0;
      width: 400px;
      height: 100vh;
      background: var(--md-default-bg-color);
      box-shadow: -2px 0 8px rgba(0,0,0,0.1);
      transform: translateX(100%);
      transition: transform 0.3s ease;
      z-index: 1000;
      display: flex;
      flex-direction: column;
    }
    
    .preferences-panel.show {
      transform: translateX(0);
    }
    
    .preferences-header {
      padding: 20px;
      border-bottom: 1px solid var(--md-default-fg-color--lightest);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    
    .preferences-header h3 {
      margin: 0;
    }
    
    .preferences-close {
      background: none;
      border: none;
      font-size: 24px;
      cursor: pointer;
      color: var(--md-default-fg-color);
    }
    
    .preferences-content {
      flex: 1;
      overflow-y: auto;
      padding: 20px;
    }
    
    .preference-group {
      margin-bottom: 30px;
    }
    
    .preference-group h4 {
      margin: 0 0 15px 0;
      color: var(--md-primary-fg-color);
    }
    
    .preference-control {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 15px;
    }
    
    .preference-control label {
      flex: 1;
      margin: 0;
    }
    
    .preference-control select {
      padding: 4px 8px;
      border: 1px solid var(--md-default-fg-color--lightest);
      border-radius: 4px;
      background: var(--md-code-bg-color);
    }
    
    .toggle-switch {
      width: 44px;
      height: 24px;
      appearance: none;
      background: var(--md-default-fg-color--lightest);
      border-radius: 12px;
      position: relative;
      cursor: pointer;
      transition: background 0.2s;
    }
    
    .toggle-switch:checked {
      background: var(--md-primary-fg-color);
    }
    
    .toggle-switch::before {
      content: '';
      position: absolute;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: white;
      top: 2px;
      left: 2px;
      transition: transform 0.2s;
    }
    
    .toggle-switch:checked::before {
      transform: translateX(20px);
    }
    
    .preferences-footer {
      padding: 20px;
      border-top: 1px solid var(--md-default-fg-color--lightest);
      display: flex;
      gap: 10px;
    }
    
    .preferences-footer button {
      flex: 1;
      padding: 8px;
      border: 1px solid var(--md-default-fg-color--lightest);
      background: var(--md-code-bg-color);
      border-radius: 4px;
      cursor: pointer;
    }
    
    .preferences-footer button:hover {
      background: var(--md-default-fg-color--lightest);
    }
    
    /* Theme-specific styles */
    [data-font-size="small"] { --md-text-font-size: 14px; }
    [data-font-size="large"] { --md-text-font-size: 18px; }
    [data-font-size="xlarge"] { --md-text-font-size: 20px; }
    
    [data-density="compact"] .md-content { padding: 0.5rem; }
    [data-density="spacious"] .md-content { padding: 1.5rem; }
    
    .no-animations * {
      animation: none !important;
      transition: none !important;
    }
    
    .reduce-motion * {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
    }
    
    .hide-line-numbers .highlight .linenodiv {
      display: none !important;
    }
    
    .hide-tooltips [data-tooltip] {
      pointer-events: none;
    }
    
    @media (max-width: 768px) {
      .preferences-panel {
        width: 100%;
      }
    }
    </style>
  `;
  
  document.head.insertAdjacentHTML('beforeend', styles);

})();