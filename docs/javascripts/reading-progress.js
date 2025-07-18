// Enhanced Reading Progress Indicator
class ReadingProgress {
  constructor() {
    this.wordsPerMinute = 200;
    this.isVisible = false;
    this.lastScrollTop = 0;
    this.createProgressBar();
    this.attachScrollListener();
    this.calculateReadingTime();
  }
  
  createProgressBar() {
    const progressBar = document.createElement('div');
    progressBar.className = 'reading-progress';
    progressBar.innerHTML = `
      <div class="reading-progress-bar">
        <div class="reading-progress-fill"></div>
      </div>
      <div class="reading-progress-info">
        <div class="progress-stats">
          <span class="progress-percentage">0%</span>
          <span class="progress-separator">•</span>
          <span class="time-remaining">Calculating...</span>
        </div>
        <button class="progress-toggle" title="Toggle progress bar">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 4.5a.5.5 0 0 1 .5.5v3.5H12a.5.5 0 0 1 0 1H8.5V13a.5.5 0 0 1-1 0V9.5H4a.5.5 0 0 1 0-1h3.5V5a.5.5 0 0 1 .5-.5z"/>
          </svg>
        </button>
      </div>
    `;
    
    document.body.appendChild(progressBar);
    
    this.progressContainer = progressBar;
    this.progressBar = progressBar.querySelector('.reading-progress-fill');
    this.progressText = progressBar.querySelector('.progress-percentage');
    this.timeText = progressBar.querySelector('.time-remaining');
    this.toggleBtn = progressBar.querySelector('.progress-toggle');
    
    // Add toggle functionality
    this.toggleBtn.addEventListener('click', () => this.toggleMinimize());
    
    // Check saved preference
    const isMinimized = localStorage.getItem('reading-progress-minimized') === 'true';
    if (isMinimized) {
      this.progressContainer.classList.add('minimized');
    }
  }
  
  attachScrollListener() {
    let ticking = false;
    let rafId = null;
    
    const updateProgress = () => {
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight - windowHeight;
      const scrollTop = window.scrollY;
      
      const progress = Math.min((scrollTop / documentHeight) * 100, 100);
      
      // Update progress bar
      this.progressBar.style.width = `${progress}%`;
      this.progressText.textContent = `${Math.round(progress)}%`;
      
      // Show/hide based on scroll
      if (scrollTop > 50 && !this.isVisible) {
        this.progressContainer.classList.add('visible');
        this.isVisible = true;
      } else if (scrollTop <= 50 && this.isVisible) {
        this.progressContainer.classList.remove('visible');
        this.isVisible = false;
      }
      
      // Update time remaining
      const content = document.querySelector('.md-content');
      if (content) {
        const remainingHeight = documentHeight - scrollTop;
        const totalHeight = documentHeight;
        const readPercentage = scrollTop / totalHeight;
        
        const totalTime = this.totalReadingTime || 10;
        const remainingTime = Math.ceil(totalTime * (1 - readPercentage));
        
        if (progress >= 100) {
          this.timeText.textContent = 'Complete! 🎉';
        } else if (remainingTime > 0) {
          this.timeText.textContent = `~${remainingTime} min left`;
        } else {
          this.timeText.textContent = 'Almost done!';
        }
      }
      
      // Scroll direction indicator
      if (scrollTop > this.lastScrollTop) {
        this.progressContainer.classList.add('scrolling-down');
        this.progressContainer.classList.remove('scrolling-up');
      } else {
        this.progressContainer.classList.add('scrolling-up');
        this.progressContainer.classList.remove('scrolling-down');
      }
      this.lastScrollTop = scrollTop;
      
      ticking = false;
    };
    
    // Throttled scroll handler for better mobile performance
    let scrollTimeout;
    const handleScroll = () => {
      if (!ticking) {
        if (rafId) cancelAnimationFrame(rafId);
        rafId = requestAnimationFrame(updateProgress);
        ticking = true;
      }
      
      // Clear existing timeout
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => {
        ticking = false;
      }, 100);
    };
    
    window.addEventListener('scroll', handleScroll, { passive: true });
    
    // Initial update
    updateProgress();
  }
  
  calculateReadingTime() {
    const content = document.querySelector('.md-content');
    if (!content) return;
    
    // Get text content and estimate word count
    const text = content.textContent || '';
    const words = text.trim().split(/\s+/).length;
    
    // Calculate reading time
    this.totalReadingTime = Math.ceil(words / this.wordsPerMinute);
    
    // Update initial display
    if (this.totalReadingTime > 0) {
      this.timeText.textContent = `~${this.totalReadingTime} min read`;
    }
  }
  
  toggleMinimize() {
    const isMinimized = this.progressContainer.classList.toggle('minimized');
    localStorage.setItem('reading-progress-minimized', isMinimized);
    
    // Update icon
    const icon = this.toggleBtn.querySelector('svg path');
    if (isMinimized) {
      icon.setAttribute('d', 'M3 8a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9A.5.5 0 0 1 3 8z');
    } else {
      icon.setAttribute('d', 'M8 4.5a.5.5 0 0 1 .5.5v3.5H12a.5.5 0 0 1 0 1H8.5V13a.5.5 0 0 1-1 0V9.5H4a.5.5 0 0 1 0-1h3.5V5a.5.5 0 0 1 .5-.5z');
    }
  }
}

// Initialize reading progress on content pages
document.addEventListener('DOMContentLoaded', () => {
  // Only show on content pages, not on homepage or tools
  const path = window.location.pathname;
  const isHomePage = path === '/' || path === '/index.html';
  const isToolsPage = path.includes('/tools/');
  const isShortPage = document.querySelector('.md-content')?.textContent?.length < 500;
  
  if (!isHomePage && !isShortPage) {
    new ReadingProgress();
  }
});