# Interview Preparation Time Allocation Calculator

## 🧮 Interactive Study Plan Generator

<div class="calculator-container">
<h3>📊 Personalized Time Allocation Calculator</h3>

<div class="calculator-inputs">
<div class="input-section">
<h4>Your Profile</h4>
<label>Current Role:
<select id="current-role">
<option value="student">Student/New Grad</option>
<option value="junior">Junior Engineer (0-2 years)</option>
<option value="mid">Mid-level (3-5 years)</option>
<option value="senior">Senior (5+ years)</option>
<option value="staff">Staff+ (8+ years)</option>
</select>
</label>

<label>Target Company:
<select id="target-company">
<option value="google">Google</option>
<option value="amazon">Amazon</option>
<option value="meta">Meta/Facebook</option>
<option value="microsoft">Microsoft</option>
<option value="apple">Apple</option>
<option value="netflix">Netflix</option>
<option value="other">Other Tech</option>
</select>
</label>

<label>Target Level:
<select id="target-level">
<option value="L3">L3/SDE I (Junior)</option>
<option value="L4">L4/SDE II (Mid)</option>
<option value="L5">L5/Senior SDE</option>
<option value="L6">L6/Staff</option>
<option value="L7">L7+/Principal</option>
</select>
</label>
</div>

<div class="input-section">
<h4>Time Availability</h4>
<label>Weeks Until Interview:
<input type="number" id="weeks-available" min="1" max="52" value="8">
</label>

<label>Hours Per Day:
<input type="number" id="hours-per-day" min="0.5" max="12" step="0.5" value="2">
</label>

<label>Days Per Week:
<input type="number" id="days-per-week" min="1" max="7" value="6">
</label>

<label>Current Preparation Level:
<input type="range" id="prep-level" min="0" max="100" value="20">
<span id="prep-level-display">20%</span>
</label>
</div>

<div class="input-section">
<h4>Strengths & Weaknesses</h4>
<label>Strongest Area:
<select id="strength">
<option value="coding">Coding/Algorithms</option>
<option value="system">System Design</option>
<option value="behavioral">Behavioral/Leadership</option>
<option value="domain">Domain Knowledge</option>
</select>
</label>

<label>Weakest Area:
<select id="weakness">
<option value="system">System Design</option>
<option value="coding">Coding/Algorithms</option>
<option value="behavioral">Behavioral/Leadership</option>
<option value="domain">Domain Knowledge</option>
</select>
</label>

<label>Learning Style:
<select id="learning-style">
<option value="visual">Visual (Videos, Diagrams)</option>
<option value="reading">Reading (Books, Blogs)</option>
<option value="practice">Practice (Hands-on)</option>
<option value="discussion">Discussion (Study Groups)</option>
</select>
</label>
</div>
</div>

<button onclick="calculateTimeAllocation()" class="calculate-btn">Generate My Study Plan</button>

<div id="results" class="results-container" style="display: none;">
<h3>📈 Your Personalized Study Plan</h3>

<div class="summary-stats">
<div class="stat-card">
<h4>Total Study Time</h4>
<p id="total-hours" class="stat-value">-</p>
</div>
<div class="stat-card">
<h4>Daily Commitment</h4>
<p id="daily-hours" class="stat-value">-</p>
</div>
<div class="stat-card">
<h4>Success Probability</h4>
<p id="success-rate" class="stat-value">-</p>
</div>
<div class="stat-card">
<h4>Readiness Date</h4>
<p id="ready-date" class="stat-value">-</p>
</div>
</div>

<div class="time-allocation-chart">
<canvas id="allocationChart" width="400" height="300"></canvas>
</div>

<div class="weekly-breakdown">
<h4>📅 Week-by-Week Focus</h4>
<div id="weekly-plan"></div>
</div>

<div class="daily-schedule">
<h4>⏰ Optimal Daily Schedule</h4>
<div id="daily-schedule"></div>
</div>

<div class="resource-recommendations">
<h4>📚 Recommended Resources</h4>
<div id="resources"></div>
</div>

<div class="milestone-tracker">
<h4>🎯 Key Milestones</h4>
<div id="milestones"></div>
</div>
</div>
</div>

## Time Allocation Strategies

### By Experience Level

```mermaid
graph LR
    subgraph "New Grad/Junior"
        NG[100% Time] --> NG1[40% Coding]
        NG --> NG2[30% System Design]
        NG --> NG3[20% Behavioral]
        NG --> NG4[10% Company Research]
    end
    
    subgraph "Mid-Level"
        ML[100% Time] --> ML1[25% Coding]
        ML --> ML2[45% System Design]
        ML --> ML3[20% Behavioral]
        ML --> ML4[10% Domain]
    end
    
    subgraph "Senior+"
        SR[100% Time] --> SR1[15% Coding]
        SR --> SR2[50% System Design]
        SR --> SR3[25% Leadership]
        SR --> SR4[10% Vision]
    end
```

### By Target Company

<div class="company-allocation">
<table class="responsive-table">
<thead>
<tr>
<th>Company</th>
<th>Coding</th>
<th>System Design</th>
<th>Behavioral</th>
<th>Special Focus</th>
</tr>
</thead>
<tbody>
<tr>
<td data-label="Company"><strong>Google</strong></td>
<td data-label="Coding">30%</td>
<td data-label="System Design">50%</td>
<td data-label="Behavioral">10%</td>
<td data-label="Special Focus">10% - Scale & Algorithms</td>
</tr>
<tr>
<td data-label="Company"><strong>Amazon</strong></td>
<td data-label="Coding">25%</td>
<td data-label="System Design">35%</td>
<td data-label="Behavioral">30%</td>
<td data-label="Special Focus">10% - Leadership Principles</td>
</tr>
<tr>
<td data-label="Company"><strong>Meta</strong></td>
<td data-label="Coding">35%</td>
<td data-label="System Design">40%</td>
<td data-label="Behavioral">15%</td>
<td data-label="Special Focus">10% - Product Sense</td>
</tr>
<tr>
<td data-label="Company"><strong>Microsoft</strong></td>
<td data-label="Coding">30%</td>
<td data-label="System Design">40%</td>
<td data-label="Behavioral">20%</td>
<td data-label="Special Focus">10% - Cloud/Enterprise</td>
</tr>
<tr>
<td data-label="Company"><strong>Apple</strong></td>
<td data-label="Coding">35%</td>
<td data-label="System Design">35%</td>
<td data-label="Behavioral">20%</td>
<td data-label="Special Focus">10% - Excellence/Details</td>
</tr>
<tr>
<td data-label="Company"><strong>Netflix</strong></td>
<td data-label="Coding">25%</td>
<td data-label="System Design">55%</td>
<td data-label="Behavioral">10%</td>
<td data-label="Special Focus">10% - Scale/Performance</td>
</tr>
</tbody>
</table>
</div>

## Quick Allocation Templates

### 2-Week Sprint (Emergency Prep)

<div class="template-grid">
<div class="template-card">
<h4>🚨 14 Days Total</h4>
<ul>
<li><strong>Days 1-3:</strong> Core concepts review</li>
<li><strong>Days 4-7:</strong> 10 system designs</li>
<li><strong>Days 8-10:</strong> Company-specific prep</li>
<li><strong>Days 11-12:</strong> Mock interviews</li>
<li><strong>Days 13-14:</strong> Polish & review</li>
</ul>
<div class="time-breakdown">
<span>Total: 56 hours @ 4hrs/day</span>
</div>
</div>

<div class="template-card">
<h4>⚡ Daily Breakdown</h4>
<ul>
<li><strong>Morning (1hr):</strong> Theory/Reading</li>
<li><strong>Afternoon (1.5hr):</strong> Practice problems</li>
<li><strong>Evening (1.5hr):</strong> System design</li>
</ul>
<div class="focus-areas">
<span>Focus: Speed > Depth</span>
</div>
</div>
</div>

### 4-Week Standard Prep

<div class="week-timeline">
<div class="timeline-week">
<h5>Week 1: Foundation</h5>
<div class="progress-bar">
<div class="progress-segment coding" style="width: 40%">Coding 40%</div>
<div class="progress-segment theory" style="width: 60%">Theory 60%</div>
</div>
</div>
<div class="timeline-week">
<h5>Week 2: Build</h5>
<div class="progress-bar">
<div class="progress-segment coding" style="width: 30%">Coding 30%</div>
<div class="progress-segment system" style="width: 70%">System Design 70%</div>
</div>
</div>
<div class="timeline-week">
<h5>Week 3: Practice</h5>
<div class="progress-bar">
<div class="progress-segment practice" style="width: 80%">Practice 80%</div>
<div class="progress-segment review" style="width: 20%">Review 20%</div>
</div>
</div>
<div class="timeline-week">
<h5>Week 4: Polish</h5>
<div class="progress-bar">
<div class="progress-segment mock" style="width: 60%">Mocks 60%</div>
<div class="progress-segment polish" style="width: 40%">Polish 40%</div>
</div>
</div>
</div>

### 8-Week Comprehensive Prep

```mermaid
gantt
    title 8-Week Preparation Timeline
    dateFormat  YYYY-MM-DD
    axisFormat  Week %U
    
    section Phase 1
    Fundamentals           :a1, 2024-01-01, 14d
    Basic Coding          :a2, 2024-01-01, 14d
    
    section Phase 2  
    Design Patterns       :b1, after a1, 14d
    Medium Problems       :b2, after a2, 14d
    
    section Phase 3
    Complex Systems       :c1, after b1, 14d
    Hard Problems         :c2, after b2, 14d
    
    section Phase 4
    Mock Interviews       :d1, after c1, 14d
    Final Polish          :d2, after c1, 14d
```

## Efficiency Maximization Tips

<div class="efficiency-grid">
<div class="tip-card">
<h4>🌅 Morning Sessions</h4>
<p><strong>Best for:</strong> Theory & Concepts</p>
<ul>
<li>Fresh mind for complex topics</li>
<li>Read papers/books</li>
<li>Watch educational videos</li>
<li>Review fundamentals</li>
</ul>
<p class="efficiency-score">Efficiency: 90%</p>
</div>

<div class="tip-card">
<h4>☀️ Afternoon Sessions</h4>
<p><strong>Best for:</strong> Coding Practice</p>
<ul>
<li>Peak problem-solving time</li>
<li>LeetCode problems</li>
<li>Algorithm practice</li>
<li>Debugging skills</li>
</ul>
<p class="efficiency-score">Efficiency: 85%</p>
</div>

<div class="tip-card">
<h4>🌆 Evening Sessions</h4>
<p><strong>Best for:</strong> System Design</p>
<ul>
<li>Creative thinking time</li>
<li>Design problems</li>
<li>Architecture planning</li>
<li>Trade-off analysis</li>
</ul>
<p class="efficiency-score">Efficiency: 80%</p>
</div>

<div class="tip-card">
<h4>🌙 Night Sessions</h4>
<p><strong>Best for:</strong> Review & Behavioral</p>
<ul>
<li>Reflect on learning</li>
<li>Behavioral stories</li>
<li>Quick reviews</li>
<li>Planning next day</li>
</ul>
<p class="efficiency-score">Efficiency: 70%</p>
</div>
</div>

## Dynamic Adjustment Framework

### Weekly Progress Checkpoints

<div class="checkpoint-system">
<div class="checkpoint">
<h4>Week 1 Check</h4>
<ul>
<li>☐ Completed fundamentals?</li>
<li>☐ 20+ coding problems?</li>
<li>☐ 2 system designs?</li>
</ul>
<p>If behind: +1 hour/day</p>
</div>

<div class="checkpoint">
<h4>Week 2 Check</h4>
<ul>
<li>☐ Patterns mastered?</li>
<li>☐ 50+ total problems?</li>
<li>☐ 5 system designs?</li>
</ul>
<p>If behind: Focus on gaps</p>
</div>

<div class="checkpoint">
<h4>Week 4 Check</h4>
<ul>
<li>☐ Mock interviews done?</li>
<li>☐ Consistent timing?</li>
<li>☐ Confidence level?</li>
</ul>
<p>If behind: Intensive mode</p>
</div>
</div>

<script>
// Update prep level display
document.getElementById('prep-level').addEventListener('input', function() {
    document.getElementById('prep-level-display').textContent = this.value + '%';
});

function calculateTimeAllocation() {
    // Get input values
    const role = document.getElementById('current-role').value;
    const company = document.getElementById('target-company').value;
    const level = document.getElementById('target-level').value;
    const weeks = parseInt(document.getElementById('weeks-available').value);
    const hoursPerDay = parseFloat(document.getElementById('hours-per-day').value);
    const daysPerWeek = parseInt(document.getElementById('days-per-week').value);
    const prepLevel = parseInt(document.getElementById('prep-level').value);
    const strength = document.getElementById('strength').value;
    const weakness = document.getElementById('weakness').value;
    const learningStyle = document.getElementById('learning-style').value;
    
    // Calculate total hours
    const totalHours = weeks * daysPerWeek * hoursPerDay;
    
    // Calculate allocation percentages based on profile
    let allocations = calculateAllocations(role, company, level, strength, weakness);
    
    // Calculate success rate
    const successRate = calculateSuccessRate(totalHours, prepLevel, weeks);
    
    // Generate weekly plan
    const weeklyPlan = generateWeeklyPlan(weeks, allocations, hoursPerDay);
    
    // Generate daily schedule
    const dailySchedule = generateDailySchedule(hoursPerDay, learningStyle);
    
    // Generate resources
    const resources = generateResources(company, level, learningStyle);
    
    // Generate milestones
    const milestones = generateMilestones(weeks, totalHours);
    
    // Display results
    displayResults(totalHours, hoursPerDay, successRate, allocations, weeklyPlan, dailySchedule, resources, milestones);
}

function calculateAllocations(role, company, level, strength, weakness) {
    // Base allocations by company
    const companyAllocations = {
        google: { coding: 30, system: 50, behavioral: 10, other: 10 },
        amazon: { coding: 25, system: 35, behavioral: 30, other: 10 },
        meta: { coding: 35, system: 40, behavioral: 15, other: 10 },
        microsoft: { coding: 30, system: 40, behavioral: 20, other: 10 },
        apple: { coding: 35, system: 35, behavioral: 20, other: 10 },
        netflix: { coding: 25, system: 55, behavioral: 10, other: 10 },
        other: { coding: 30, system: 45, behavioral: 15, other: 10 }
    };
    
    let allocation = { ...companyAllocations[company] };
    
    // Adjust for weakness (increase by 10%)
    if (weakness === 'coding') allocation.coding += 10;
    else if (weakness === 'system') allocation.system += 10;
    else if (weakness === 'behavioral') allocation.behavioral += 10;
    
    // Adjust for strength (decrease by 5%)
    if (strength === 'coding') allocation.coding -= 5;
    else if (strength === 'system') allocation.system -= 5;
    else if (strength === 'behavioral') allocation.behavioral -= 5;
    
    // Normalize to 100%
    const total = allocation.coding + allocation.system + allocation.behavioral + allocation.other;
    Object.keys(allocation).forEach(key => {
        allocation[key] = Math.round((allocation[key] / total) * 100);
    });
    
    return allocation;
}

function calculateSuccessRate(totalHours, prepLevel, weeks) {
    // Base success rate calculation
    let successRate = prepLevel;
    
    // Add points for study hours
    if (totalHours >= 200) successRate += 30;
    else if (totalHours >= 100) successRate += 20;
    else if (totalHours >= 50) successRate += 10;
    
    // Add points for preparation time
    if (weeks >= 8) successRate += 15;
    else if (weeks >= 4) successRate += 10;
    else if (weeks >= 2) successRate += 5;
    
    return Math.min(95, successRate);
}

function generateWeeklyPlan(weeks, allocations, hoursPerDay) {
    const phases = [];
    
    if (weeks >= 8) {
        phases.push(
            { week: '1-2', focus: 'Fundamentals', details: 'Theory, basics, easy problems' },
            { week: '3-4', focus: 'Core Skills', details: 'Patterns, medium problems' },
            { week: '5-6', focus: 'Advanced', details: 'Complex systems, hard problems' },
            { week: '7-8', focus: 'Polish', details: 'Mocks, weak areas, final prep' }
        );
    } else if (weeks >= 4) {
        phases.push(
            { week: '1', focus: 'Essentials', details: 'Core concepts, patterns' },
            { week: '2', focus: 'Practice', details: 'System design, coding' },
            { week: '3', focus: 'Company Focus', details: 'Target company prep' },
            { week: '4', focus: 'Final Prep', details: 'Mocks and polish' }
        );
    } else {
        phases.push(
            { week: '1', focus: 'Crash Course', details: 'Essential concepts only' },
            { week: '2', focus: 'Intensive Practice', details: 'Core problems and mocks' }
        );
    }
    
    return phases;
}

function generateDailySchedule(hoursPerDay, learningStyle) {
    const schedules = {
        visual: [
            { time: 'First 30%', activity: 'Watch videos/lectures', focus: 'Visual learning' },
            { time: 'Middle 50%', activity: 'Practice with diagrams', focus: 'Apply concepts' },
            { time: 'Last 20%', activity: 'Review visual notes', focus: 'Retention' }
        ],
        reading: [
            { time: 'First 40%', activity: 'Read books/blogs', focus: 'Deep understanding' },
            { time: 'Middle 40%', activity: 'Practice problems', focus: 'Application' },
            { time: 'Last 20%', activity: 'Take notes', focus: 'Synthesis' }
        ],
        practice: [
            { time: 'First 20%', activity: 'Quick theory review', focus: 'Context' },
            { time: 'Middle 60%', activity: 'Hands-on practice', focus: 'Skills building' },
            { time: 'Last 20%', activity: 'Reflect on learning', focus: 'Improvement' }
        ],
        discussion: [
            { time: 'First 30%', activity: 'Study group prep', focus: 'Preparation' },
            { time: 'Middle 50%', activity: 'Mock interviews', focus: 'Interactive learning' },
            { time: 'Last 20%', activity: 'Feedback review', focus: 'Growth' }
        ]
    };
    
    return schedules[learningStyle];
}

function generateResources(company, level, learningStyle) {
    const resources = {
        visual: [
            { type: 'Video', name: 'System Design Interview - YouTube', url: '#' },
            { type: 'Course', name: 'Grokking System Design', url: '#' },
            { type: 'Diagrams', name: 'Draw.io Templates', url: '#' }
        ],
        reading: [
            { type: 'Book', name: 'DDIA - Kleppmann', url: '#' },
            { type: 'Blog', name: 'High Scalability', url: '#' },
            { type: 'Papers', name: `${company} Research Papers`, url: '#' }
        ],
        practice: [
            { type: 'Platform', name: 'LeetCode', url: '#' },
            { type: 'Mock', name: 'Pramp', url: '#' },
            { type: 'Projects', name: 'Build Mini Systems', url: '#' }
        ],
        discussion: [
            { type: 'Community', name: 'Blind Forums', url: '#' },
            { type: 'Groups', name: 'Local Study Groups', url: '#' },
            { type: 'Mentorship', name: 'Interview Coaches', url: '#' }
        ]
    };
    
    return resources[learningStyle];
}

function generateMilestones(weeks, totalHours) {
    const milestones = [];
    
    if (weeks >= 8) {
        milestones.push(
            { week: 2, goal: 'Complete fundamentals', metric: '20 easy problems solved' },
            { week: 4, goal: 'Master patterns', metric: '10 system designs completed' },
            { week: 6, goal: 'Advanced skills', metric: '5 complex systems designed' },
            { week: 8, goal: 'Interview ready', metric: '10 mock interviews passed' }
        );
    } else if (weeks >= 4) {
        milestones.push(
            { week: 1, goal: 'Core concepts', metric: '10 problems solved' },
            { week: 2, goal: 'Practice phase', metric: '5 systems designed' },
            { week: 3, goal: 'Company focus', metric: '3 mock interviews' },
            { week: 4, goal: 'Final polish', metric: 'Consistent performance' }
        );
    } else {
        milestones.push(
            { week: 1, goal: 'Essentials covered', metric: 'Key concepts understood' },
            { week: 2, goal: 'Ready to interview', metric: '2 mock interviews completed' }
        );
    }
    
    return milestones;
}

function displayResults(totalHours, hoursPerDay, successRate, allocations, weeklyPlan, dailySchedule, resources, milestones) {
    // Update summary stats
    document.getElementById('total-hours').textContent = `${totalHours} hours`;
    document.getElementById('daily-hours').textContent = `${hoursPerDay} hours`;
    document.getElementById('success-rate').textContent = `${successRate}%`;
    
    const readyDate = new Date();
    readyDate.setDate(readyDate.getDate() + (parseInt(document.getElementById('weeks-available').value) * 7));
    document.getElementById('ready-date').textContent = readyDate.toLocaleDateString();
    
    // Draw allocation chart
    drawAllocationChart(allocations);
    
    // Display weekly plan
    let weeklyHtml = '<div class="week-plan">';
    weeklyPlan.forEach(phase => {
        weeklyHtml += `
            <div class="week-item">
                <h5>Week ${phase.week}: ${phase.focus}</h5>
                <p>${phase.details}</p>
            </div>
        `;
    });
    weeklyHtml += '</div>';
    document.getElementById('weekly-plan').innerHTML = weeklyHtml;
    
    // Display daily schedule
    let scheduleHtml = '<div class="schedule-items">';
    dailySchedule.forEach(slot => {
        scheduleHtml += `
            <div class="schedule-item">
                <span class="time">${slot.time}</span>
                <span class="activity">${slot.activity}</span>
                <span class="focus">${slot.focus}</span>
            </div>
        `;
    });
    scheduleHtml += '</div>';
    document.getElementById('daily-schedule').innerHTML = scheduleHtml;
    
    // Display resources
    let resourcesHtml = '<div class="resource-list">';
    resources.forEach(resource => {
        resourcesHtml += `
            <div class="resource-item">
                <span class="resource-type">${resource.type}:</span>
                <a href="${resource.url}">${resource.name}</a>
            </div>
        `;
    });
    resourcesHtml += '</div>';
    document.getElementById('resources').innerHTML = resourcesHtml;
    
    // Display milestones
    let milestonesHtml = '<div class="milestone-list">';
    milestones.forEach(milestone => {
        milestonesHtml += `
            <div class="milestone-item">
                <span class="week">Week ${milestone.week}</span>
                <span class="goal">${milestone.goal}</span>
                <span class="metric">${milestone.metric}</span>
            </div>
        `;
    });
    milestonesHtml += '</div>';
    document.getElementById('milestones').innerHTML = milestonesHtml;
    
    // Show results
    document.getElementById('results').style.display = 'block';
}

function drawAllocationChart(allocations) {
    const canvas = document.getElementById('allocationChart');
    const ctx = canvas.getContext('2d');
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Data
    const data = [
        { label: 'Coding', value: allocations.coding, color: '#4285F4' },
        { label: 'System Design', value: allocations.system, color: '#34A853' },
        { label: 'Behavioral', value: allocations.behavioral, color: '#FBBC04' },
        { label: 'Other', value: allocations.other, color: '#EA4335' }
    ];
    
    // Calculate angles
    let currentAngle = -Math.PI / 2;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = 100;
    
    // Draw pie chart
    data.forEach(segment => {
        const angle = (segment.value / 100) * Math.PI * 2;
        
        // Draw segment
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + angle);
        ctx.closePath();
        ctx.fillStyle = segment.color;
        ctx.fill();
        
        // Draw label
        const labelAngle = currentAngle + angle / 2;
        const labelX = centerX + Math.cos(labelAngle) * (radius + 20);
        const labelY = centerY + Math.sin(labelAngle) * (radius + 20);
        
        ctx.fillStyle = '#333';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`${segment.label}: ${segment.value}%`, labelX, labelY);
        
        currentAngle += angle;
    });
}
</script>

