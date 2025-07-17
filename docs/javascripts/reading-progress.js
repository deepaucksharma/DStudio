// Reading Progress Indicator
class ReadingProgress {
  constructor() {
    this.createProgressBar();
    this.attachScrollListener();
  }
  
  createProgressBar() {
    const progressBar = document.createElement('div');
    progressBar.className = 'reading-progress';
    progressBar.innerHTML = `
      <div class="reading-progress-bar"></div>
      <div class="reading-progress-text">
        <span class="progress-percentage">0%</span>
        <span class="time-remaining">~15 min left</span>
      </div>
    `;
    
    document.body.appendChild(progressBar);
    
    this.progressBar = progressBar.querySelector('.reading-progress-bar');
    this.progressText = progressBar.querySelector('.progress-percentage');
    this.timeText = progressBar.querySelector('.time-remaining');
  }
  
  attachScrollListener() {
    let ticking = false;
    
    const updateProgress = () => {
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight - windowHeight;
      const scrollTop = window.scrollY;
      
      const progress = Math.min((scrollTop / documentHeight) * 100, 100);
      
      this.progressBar.style.width = `${progress}%`;
      this.progressText.textContent = `${Math.round(progress)}%`;
      
      // Update time remaining
      const wordsPerMinute = 200;
      const remainingHeight = documentHeight - scrollTop;
      const remainingWords = (remainingHeight / windowHeight) * 500; // Estimate
      const remainingMinutes = Math.ceil(remainingWords / wordsPerMinute);
      
      if (remainingMinutes > 0) {
        this.timeText.textContent = `~${remainingMinutes} min left`;
      } else {
        this.timeText.textContent = 'Complete!';
      }
      
      ticking = false;
    };
    
    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(updateProgress);
        ticking = true;
      }
    });
    
    // Initial update
    updateProgress();
  }
}

// Initialize reading progress on content pages
document.addEventListener('DOMContentLoaded', () => {
  // Only show on content pages, not on homepage
  if (!window.location.pathname.match(/^\/?$/) && !window.location.pathname.includes('/tools/')) {
    new ReadingProgress();
  }
});