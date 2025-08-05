# Your Learning Progress

<div class="progress-dashboard">

## Progress Overview

<div class="progress-overview">
    <div class="progress-card">
        <div class="progress-ring">
            <svg width="200" height="200">
                <circle cx="100" cy="100" r="80" class="progress-ring-bg"></circle>
                <circle cx="100" cy="100" r="80" class="progress-ring-fill" 
                        stroke-dasharray="502.65" 
                        stroke-dashoffset="502.65"
                        id="overall-progress-ring"></circle>
            </svg>
            <div class="progress-ring-text" id="overall-percentage">0%</div>
        </div>
        <div class="progress-card-label">Overall Progress</div>
    </div>
    
    <div class="progress-card">
        <div class="progress-card-value" id="pages-completed">0</div>
        <div class="progress-card-label">Pages Completed</div>
    </div>
    
    <div class="progress-card">
        <div class="progress-card-value" id="reading-time">0h 0m</div>
        <div class="progress-card-label">Total Reading Time</div>
    </div>
    
    <div class="progress-card">
        <div class="progress-card-value" id="current-streak">0</div>
        <div class="progress-card-label">Day Streak</div>
    </div>
</div>

## Progress by Category

<div class="progress-categories" id="category-progress">
    <!-- Categories will be populated by JavaScript -->
</div>

## Achievements

<div class="achievements-grid" id="achievements-grid">
    <!-- Achievements will be populated by JavaScript -->
</div>

## Progress Controls

<div class="progress-controls">
    <button class="progress-button" onclick="progressTracker.exportProgress()">
        Export Progress
    </button>
    <input type="file" id="import-file" style="display: none" accept=".json" 
           onchange="progressTracker.importProgress(this.files[0])">
    <button class="progress-button" onclick="document.getElementById('import-file').click()">
        Import Progress
    </button>
    <button class="progress-button danger" onclick="progressTracker.resetProgress()">
        Reset Progress
    </button>
</div>

</div>

<script>
// Progress dashboard initialization
document.addEventListener('DOMContentLoaded', function() {
    if (!window.progressTracker) return;
    
    const progress = progressTracker.progress;
    const totalPages = document.querySelectorAll('.md-nav__link').length || 200; // Estimate
    
    // Update overview cards
    const percentage = Math.round((progress.completedPages.length / totalPages) * 100);
    document.getElementById('overall-percentage').textContent = percentage + '%';
    document.getElementById('pages-completed').textContent = progress.completedPages.length;
    
    // Update progress ring
    const ring = document.getElementById('overall-progress-ring');
    const circumference = 2 * Math.PI * 80; // radius = 80
    const offset = circumference - (percentage / 100) * circumference;
    ring.style.strokeDashoffset = offset;
    
    // Format reading time
    const hours = Math.floor(progress.totalReadingTime / 3600000);
    const minutes = Math.floor((progress.totalReadingTime % 3600000) / 60000);
    document.getElementById('reading-time').textContent = `${hours}h ${minutes}m`;
    
    // Calculate streak (simplified - checks if visited today)
    const today = new Date().toDateString();
    const lastVisit = new Date(progress.lastVisit).toDateString();
    const streak = today === lastVisit ? 1 : 0; // Simplified for demo
    document.getElementById('current-streak').textContent = streak;
    
    // Category progress
    const categories = [
        { name: 'Fundamental Axioms', path: '/part1-axioms/', total: 7 },
        { name: 'Foundational Pillars', path: '/part2-pillars/', total: 5 },
        { name: 'Patterns', path: '/pattern-library/', total: 91 },
        { name: 'Quantitative Toolkit', path: '/quantitative/', total: 10 },
        { name: 'Human Factors', path: '/human-factors/', total: 15 },
        { name: 'Excellence Framework', path: '/excellence/', total: 8 }
    ];
    
    const categoryHTML = categories.map(cat => {
        const completed = progress.completedPages.filter(p => p.includes(cat.path)).length;
        const percentage = Math.round((completed / cat.total) * 100);
        
        return `
            <div class="category-progress">
                <div class="category-header">
                    <span class="category-name">${cat.name}</span>
                    <span class="category-stats">${completed} / ${cat.total}</span>
                </div>
                <div class="category-bar">
                    <div class="category-bar-fill" style="width: ${percentage}%">
                        <span class="category-bar-text">${percentage}%</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    document.getElementById('category-progress').innerHTML = categoryHTML;
    
    // Achievements
    const allAchievements = [
        { id: 'first-page', icon: '🎯', title: 'First Steps', description: 'Complete your first page' },
        { id: 'getting-started', icon: '🚀', title: 'Getting Started', description: 'Complete 5 pages' },
        { id: 'making-progress', icon: '📈', title: 'Making Progress', description: 'Complete 10 pages' },
        { id: 'quarter-way', icon: '🌟', title: 'Quarter Way', description: 'Complete 25 pages' },
        { id: 'half-way', icon: '⭐', title: 'Halfway There', description: 'Complete 50 pages' },
        { id: 'completionist', icon: '🏆', title: 'Completionist', description: 'Complete 100 pages' },
        { id: 'axiom-master', icon: '🔮', title: 'Axiom Master', description: 'Complete all 7 fundamental axioms' },
        { id: 'pillar-expert', icon: '🏛️', title: 'Pillar Expert', description: 'Complete all 5 foundational pillars' },
        { id: 'pattern-explorer', icon: '🗺️', title: 'Pattern Explorer', description: 'Explore 20 patterns' }
    ];
    
    const achievementsHTML = allAchievements.map(achievement => {
        const earned = progress.achievements.includes(achievement.id);
        
        return `
            <div class="achievement-card ${earned ? 'earned' : 'locked'}">
                <div class="achievement-card-header">
                    <span class="achievement-card-icon">${achievement.icon}</span>
                    <span class="achievement-card-title">${achievement.title}</span>
                </div>
                <div class="achievement-card-description">${achievement.description}</div>
            </div>
        `;
    }).join('');
    
    document.getElementById('achievements-grid').innerHTML = achievementsHTML;
});
</script>