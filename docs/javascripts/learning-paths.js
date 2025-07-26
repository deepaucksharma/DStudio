// Learning Path Visual Connections and Progress Tracking
document.addEventListener('DOMContentLoaded', function() {
    // Add visual learning path indicators
    const addLearningPathIndicators = () => {
        // Find all learning path navigation elements
        const pathElements = document.querySelectorAll('.learning-path-nav');
        
        pathElements.forEach(elem => {
            const progress = elem.getAttribute('data-progress') || '0';
            const difficulty = elem.getAttribute('data-difficulty') || 'medium';
            
            // Add progress bar
            const progressBar = document.createElement('div');
            progressBar.className = 'learning-progress-bar';
            progressBar.innerHTML = `
                <div class="progress-fill" style="width: ${progress}%"></div>
                <span class="progress-text">${progress}% Complete</span>
            `;
            elem.appendChild(progressBar);
            
            // Add difficulty indicator
            const difficultyBadge = document.createElement('span');
            difficultyBadge.className = `difficulty-badge difficulty-${difficulty}`;
            difficultyBadge.textContent = difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
            elem.appendChild(difficultyBadge);
        });
    };
    
    // Create learning path connections visualization
    const createPathConnections = () => {
        const connectionsContainer = document.querySelector('.learning-connections');
        if (!connectionsContainer) return;
        
        // Define connections between topics
        const connections = [
            { from: 'laws', to: 'pillars', label: 'Theory → Practice' },
            { from: 'pillars', to: 'patterns', label: 'Strategy → Tactics' },
            { from: 'patterns', to: 'case-studies', label: 'Tactics → Reality' }
        ];
        
        // Create SVG for connections
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('class', 'learning-path-connections');
        
        connections.forEach(conn => {
            const fromElem = document.getElementById(`path-${conn.from}`);
            const toElem = document.getElementById(`path-${conn.to}`);
            
            if (fromElem && toElem) {
                const fromRect = fromElem.getBoundingClientRect();
                const toRect = toElem.getBoundingClientRect();
                
                // Create path element
                const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                const d = `M ${fromRect.right} ${fromRect.top + fromRect.height/2} 
                           C ${fromRect.right + 50} ${fromRect.top + fromRect.height/2},
                             ${toRect.left - 50} ${toRect.top + toRect.height/2},
                             ${toRect.left} ${toRect.top + toRect.height/2}`;
                path.setAttribute('d', d);
                path.setAttribute('class', 'connection-path');
                
                // Add label
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', (fromRect.right + toRect.left) / 2);
                text.setAttribute('y', (fromRect.bottom + toRect.top) / 2);
                text.setAttribute('class', 'connection-label');
                text.textContent = conn.label;
                
                svg.appendChild(path);
                svg.appendChild(text);
            }
        });
        
        connectionsContainer.appendChild(svg);
    };
    
    // Add time estimates and difficulty indicators
    const addTimeEstimates = () => {
        const timeElements = document.querySelectorAll('[data-time-estimate]');
        
        timeElements.forEach(elem => {
            const time = elem.getAttribute('data-time-estimate');
            const timeDisplay = document.createElement('div');
            timeDisplay.className = 'time-estimate';
            timeDisplay.innerHTML = `
                <span class="time-icon">⏱️</span>
                <span class="time-text">${time}</span>
            `;
            elem.appendChild(timeDisplay);
        });
    };
    
    // Track reading progress
    const trackProgress = () => {
        const sections = document.querySelectorAll('.learning-section');
        const progressKey = 'learning-progress';
        let progress = JSON.parse(localStorage.getItem(progressKey) || '{}');
        
        // Mark sections as complete when scrolled into view
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const sectionId = entry.target.getAttribute('data-section-id');
                    if (sectionId && !progress[sectionId]) {
                        progress[sectionId] = {
                            completed: true,
                            timestamp: new Date().toISOString()
                        };
                        localStorage.setItem(progressKey, JSON.stringify(progress));
                        updateProgressDisplay();
                    }
                }
            });
        }, { threshold: 0.8 });
        
        sections.forEach(section => observer.observe(section));
    };
    
    // Update progress display
    const updateProgressDisplay = () => {
        const progressKey = 'learning-progress';
        const progress = JSON.parse(localStorage.getItem(progressKey) || '{}');
        const totalSections = document.querySelectorAll('.learning-section').length;
        const completedSections = Object.keys(progress).length;
        const percentComplete = Math.round((completedSections / totalSections) * 100);
        
        const progressDisplay = document.querySelector('.overall-progress');
        if (progressDisplay) {
            progressDisplay.innerHTML = `
                <h3>Your Progress</h3>
                <div class="progress-ring">
                    <svg width="120" height="120">
                        <circle cx="60" cy="60" r="50" class="progress-ring-bg"></circle>
                        <circle cx="60" cy="60" r="50" class="progress-ring-fill" 
                                style="stroke-dasharray: ${314 * percentComplete / 100} 314"></circle>
                    </svg>
                    <div class="progress-percent">${percentComplete}%</div>
                </div>
                <p>${completedSections} of ${totalSections} sections completed</p>
            `;
        }
    };
    
    // Initialize all features
    addLearningPathIndicators();
    createPathConnections();
    addTimeEstimates();
    trackProgress();
    updateProgressDisplay();
});

// Add corresponding CSS
const style = document.createElement('style');
style.textContent = `
    /* Learning Progress Bar */
    .learning-progress-bar {
        width: 100%;
        height: 8px;
        background-color: #e0e0e0;
        border-radius: 4px;
        margin-top: 8px;
        position: relative;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #5448C8 0%, #00BCD4 100%);
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    
    .progress-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 10px;
        font-weight: bold;
        color: #333;
    }
    
    /* Difficulty Badges */
    .difficulty-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 8px;
    }
    
    .difficulty-easy {
        background-color: #4caf50;
        color: white;
    }
    
    .difficulty-medium {
        background-color: #ff9800;
        color: white;
    }
    
    .difficulty-hard {
        background-color: #f44336;
        color: white;
    }
    
    /* Learning Path Connections */
    .learning-path-connections {
        width: 100%;
        height: 200px;
        margin: 20px 0;
    }
    
    .connection-path {
        fill: none;
        stroke: #5448C8;
        stroke-width: 2;
        stroke-dasharray: 5,5;
        opacity: 0.6;
    }
    
    .connection-label {
        font-size: 12px;
        fill: #666;
        text-anchor: middle;
    }
    
    /* Time Estimates */
    .time-estimate {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 8px;
        background-color: #f5f5f5;
        border-radius: 4px;
        font-size: 14px;
        margin-top: 8px;
    }
    
    .time-icon {
        font-size: 16px;
    }
    
    /* Progress Ring */
    .progress-ring {
        position: relative;
        display: inline-block;
    }
    
    .progress-ring-bg {
        fill: none;
        stroke: #e0e0e0;
        stroke-width: 8;
    }
    
    .progress-ring-fill {
        fill: none;
        stroke: #5448C8;
        stroke-width: 8;
        stroke-linecap: round;
        transform: rotate(-90deg);
        transform-origin: center;
        transition: stroke-dasharray 0.3s ease;
    }
    
    .progress-percent {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 24px;
        font-weight: bold;
        color: #5448C8;
    }
    
    /* Overall Progress Display */
    .overall-progress {
        text-align: center;
        padding: 20px;
        background-color: #f8f9fa;
        border-radius: 8px;
        margin: 20px 0;
    }
    
    .overall-progress h3 {
        margin-bottom: 16px;
        color: #333;
    }
    
    .overall-progress p {
        margin-top: 12px;
        color: #666;
    }
`;
document.head.appendChild(style);