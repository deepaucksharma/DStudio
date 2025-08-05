/**
 * Progress Tracker for The Compendium of Distributed Systems
 * Tracks user reading progress across the entire site
 */

class ProgressTracker {
    constructor() {
        this.STORAGE_KEY = 'dstudio-progress';
        this.progress = this.loadProgress();
        this.currentPath = '';
        
        // Initialize on DOM ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    init() {
        // Track current page
        this.currentPath = this.getCurrentPath();
        this.trackPageVisit();
        
        // Set up page visibility tracking
        this.trackReadingTime();
        
        // Update navigation UI
        this.updateNavigationUI();
        
        // Add progress summary to header
        this.addProgressSummary();
        
        // Listen for navigation changes (MkDocs Material uses instant loading)
        document.addEventListener('DOMContentLoaded', () => this.onPageChange());
        document.addEventListener('contentupdate', () => this.onPageChange());
        
        // Save progress periodically
        setInterval(() => this.saveProgress(), 30000); // Every 30 seconds
        
        // Save on page unload
        window.addEventListener('beforeunload', () => this.saveProgress());
    }

    getCurrentPath() {
        // Get path relative to site root
        const path = window.location.pathname.replace(/\/$/, '');
        const basePath = '/DStudio';
        return path.startsWith(basePath) ? path.substring(basePath.length) : path;
    }

    loadProgress() {
        try {
            const saved = localStorage.getItem(this.STORAGE_KEY);
            return saved ? JSON.parse(saved) : this.getDefaultProgress();
        } catch (e) {
            console.error('Failed to load progress:', e);
            return this.getDefaultProgress();
        }
    }

    getDefaultProgress() {
        return {
            visitedPages: {},
            completedPages: [],
            totalReadingTime: 0,
            lastVisit: new Date().toISOString(),
            startDate: new Date().toISOString(),
            achievements: []
        };
    }

    saveProgress() {
        try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(this.progress));
        } catch (e) {
            console.error('Failed to save progress:', e);
        }
    }

    trackPageVisit() {
        if (!this.currentPath) return;
        
        // Initialize page data if not exists
        if (!this.progress.visitedPages[this.currentPath]) {
            this.progress.visitedPages[this.currentPath] = {
                firstVisit: new Date().toISOString(),
                lastVisit: new Date().toISOString(),
                visitCount: 0,
                readingTime: 0,
                completed: false,
                scrollProgress: 0
            };
        }
        
        const pageData = this.progress.visitedPages[this.currentPath];
        pageData.visitCount++;
        pageData.lastVisit = new Date().toISOString();
        this.progress.lastVisit = new Date().toISOString();
        
        this.saveProgress();
    }

    trackReadingTime() {
        let startTime = Date.now();
        let isVisible = !document.hidden;
        
        // Track scroll progress
        let ticking = false;
        const updateScrollProgress = () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
                    const scrollProgress = scrollHeight > 0 ? (window.scrollY / scrollHeight) * 100 : 0;
                    
                    if (this.progress.visitedPages[this.currentPath]) {
                        this.progress.visitedPages[this.currentPath].scrollProgress = Math.max(
                            this.progress.visitedPages[this.currentPath].scrollProgress || 0,
                            scrollProgress
                        );
                        
                        // Mark as completed if scrolled > 80%
                        if (scrollProgress > 80 && !this.progress.visitedPages[this.currentPath].completed) {
                            this.markPageCompleted(this.currentPath);
                        }
                    }
                    ticking = false;
                });
                ticking = true;
            }
        };
        
        window.addEventListener('scroll', updateScrollProgress);
        updateScrollProgress(); // Initial check
        
        // Track active reading time
        const updateReadingTime = () => {
            if (isVisible && this.progress.visitedPages[this.currentPath]) {
                const elapsed = Date.now() - startTime;
                this.progress.visitedPages[this.currentPath].readingTime += elapsed;
                this.progress.totalReadingTime += elapsed;
            }
            startTime = Date.now();
        };
        
        // Update reading time when visibility changes
        document.addEventListener('visibilitychange', () => {
            updateReadingTime();
            isVisible = !document.hidden;
        });
        
        // Update reading time periodically
        setInterval(() => {
            if (isVisible) updateReadingTime();
        }, 10000); // Every 10 seconds
    }

    markPageCompleted(path) {
        if (!this.progress.completedPages.includes(path)) {
            this.progress.completedPages.push(path);
            if (this.progress.visitedPages[path]) {
                this.progress.visitedPages[path].completed = true;
            }
            this.checkAchievements();
            this.updateNavigationUI();
            this.saveProgress();
        }
    }

    checkAchievements() {
        const achievements = [];
        const completed = this.progress.completedPages.length;
        
        // Milestone achievements
        const milestones = [
            { count: 1, id: 'first-page', title: 'First Steps', description: 'Completed your first page' },
            { count: 5, id: 'getting-started', title: 'Getting Started', description: 'Completed 5 pages' },
            { count: 10, id: 'making-progress', title: 'Making Progress', description: 'Completed 10 pages' },
            { count: 25, id: 'quarter-way', title: 'Quarter Way', description: 'Completed 25 pages' },
            { count: 50, id: 'half-way', title: 'Halfway There', description: 'Completed 50 pages' },
            { count: 100, id: 'completionist', title: 'Completionist', description: 'Completed 100 pages' }
        ];
        
        milestones.forEach(milestone => {
            if (completed >= milestone.count && !this.progress.achievements.includes(milestone.id)) {
                this.progress.achievements.push(milestone.id);
                this.showAchievement(milestone);
            }
        });
        
        // Category achievements
        const axiomPages = this.progress.completedPages.filter(p => p.includes('/part1-axioms/'));
        const pillarPages = this.progress.completedPages.filter(p => p.includes('/part2-pillars/'));
        const patternPages = this.progress.completedPages.filter(p => p.includes('/pattern-library/'));
        
        if (axiomPages.length >= 7 && !this.progress.achievements.includes('axiom-master')) {
            this.progress.achievements.push('axiom-master');
            this.showAchievement({ id: 'axiom-master', title: 'Axiom Master', description: 'Completed all 7 fundamental axioms' });
        }
        
        if (pillarPages.length >= 5 && !this.progress.achievements.includes('pillar-expert')) {
            this.progress.achievements.push('pillar-expert');
            this.showAchievement({ id: 'pillar-expert', title: 'Pillar Expert', description: 'Completed all 5 foundational pillars' });
        }
        
        if (patternPages.length >= 20 && !this.progress.achievements.includes('pattern-explorer')) {
            this.progress.achievements.push('pattern-explorer');
            this.showAchievement({ id: 'pattern-explorer', title: 'Pattern Explorer', description: 'Explored 20 patterns' });
        }
    }

    showAchievement(achievement) {
        // Create achievement notification
        const notification = document.createElement('div');
        notification.className = 'achievement-notification';
        notification.innerHTML = `
            <div class="achievement-icon">🏆</div>
            <div class="achievement-content">
                <div class="achievement-title">${achievement.title}</div>
                <div class="achievement-description">${achievement.description}</div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Remove after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    updateNavigationUI() {
        // Add completion checkmarks to navigation items
        const navLinks = document.querySelectorAll('.md-nav__link');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (!href) return;
            
            // Convert href to path format
            const path = href.replace(/^\.\./, '').replace(/\/$/, '').replace(/\.html$/, '');
            
            // Check if page is completed
            if (this.progress.completedPages.includes(path)) {
                if (!link.querySelector('.progress-check')) {
                    const check = document.createElement('span');
                    check.className = 'progress-check';
                    check.innerHTML = '✓';
                    link.appendChild(check);
                }
            }
            
            // Add visit indicator
            if (this.progress.visitedPages[path]) {
                link.classList.add('visited');
                
                // Add reading progress indicator
                const progress = this.progress.visitedPages[path].scrollProgress || 0;
                if (progress > 0 && progress < 80) {
                    const indicator = link.querySelector('.progress-indicator') || document.createElement('span');
                    indicator.className = 'progress-indicator';
                    indicator.style.width = `${progress}%`;
                    if (!link.querySelector('.progress-indicator')) {
                        link.appendChild(indicator);
                    }
                }
            }
        });
    }

    addProgressSummary() {
        // Add progress summary to header if not exists
        if (document.querySelector('.progress-summary')) return;
        
        const header = document.querySelector('.md-header__inner');
        if (!header) return;
        
        const summary = document.createElement('div');
        summary.className = 'progress-summary';
        summary.innerHTML = this.getProgressSummaryHTML();
        
        header.appendChild(summary);
    }

    getProgressSummaryHTML() {
        const totalPages = document.querySelectorAll('.md-nav__link').length;
        const completedCount = this.progress.completedPages.length;
        const visitedCount = Object.keys(this.progress.visitedPages).length;
        const percentage = totalPages > 0 ? Math.round((completedCount / totalPages) * 100) : 0;
        const readingHours = Math.floor(this.progress.totalReadingTime / 3600000);
        const readingMinutes = Math.floor((this.progress.totalReadingTime % 3600000) / 60000);
        
        return `
            <div class="progress-stats">
                <span class="progress-stat">
                    <span class="progress-label">Progress</span>
                    <span class="progress-value">${percentage}%</span>
                </span>
                <span class="progress-stat">
                    <span class="progress-label">Completed</span>
                    <span class="progress-value">${completedCount}/${totalPages}</span>
                </span>
                <span class="progress-stat">
                    <span class="progress-label">Reading Time</span>
                    <span class="progress-value">${readingHours}h ${readingMinutes}m</span>
                </span>
                <a href="/DStudio/progress/" class="progress-dashboard-link" title="View detailed progress">
                    <span class="twemoji">📊</span>
                </a>
            </div>
        `;
    }

    onPageChange() {
        this.currentPath = this.getCurrentPath();
        this.trackPageVisit();
        this.updateNavigationUI();
        this.addProgressSummary();
    }

    // Public API for manual marking
    markCurrentPageComplete() {
        this.markPageCompleted(this.currentPath);
    }

    resetProgress() {
        if (confirm('Are you sure you want to reset all your progress? This cannot be undone.')) {
            this.progress = this.getDefaultProgress();
            this.saveProgress();
            location.reload();
        }
    }

    exportProgress() {
        const data = {
            progress: this.progress,
            exportDate: new Date().toISOString(),
            site: 'The Compendium of Distributed Systems'
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dstudio-progress-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    importProgress(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);
                if (data.progress && data.site === 'The Compendium of Distributed Systems') {
                    this.progress = data.progress;
                    this.saveProgress();
                    location.reload();
                } else {
                    alert('Invalid progress file');
                }
            } catch (err) {
                alert('Failed to import progress file');
            }
        };
        reader.readAsText(file);
    }
}

// Initialize progress tracker
window.progressTracker = new ProgressTracker();