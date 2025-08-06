---
title: Pattern Health Dashboard
description: .health-dashboard { padding: 24px; max-width: 1400px; margin: 0 auto; }
type: reference
---

# Pattern Health Dashboard

<div class="health-dashboard">
  <div class="dashboard-header">
    <h2>📊 Pattern Health Metrics</h2>
    <div class="last-updated">Last Updated: <span id="last-updated-time">Loading...</span></div>
    <div class="filter-controls">
      <button class="tier-filter active" data-tier="all">All Patterns</button>
      <button class="tier-filter" data-tier="gold">🏆 Gold</button>
      <button class="tier-filter" data-tier="silver">🥈 Silver</button>
      <button class="tier-filter" data-tier="bronze">🥉 Bronze</button>
    </div>
  </div>

  <div class="health-summary cards">
    <div class="health-card gold-card">
      <h3>🏆 Gold Patterns</h3>
      <div class="metric-value" id="gold-count">38</div>
      <div class="metric-label">Total Patterns</div>
      <div class="health-avg" id="gold-health-avg">Loading...</div>
    </div>
    <div class="health-card silver-card">
      <h3>🥈 Silver Patterns</h3>
      <div class="metric-value" id="silver-count">38</div>
      <div class="metric-label">Total Patterns</div>
      <div class="health-avg" id="silver-health-avg">Loading...</div>
    </div>
    <div class="health-card bronze-card">
      <h3>🥉 Bronze Patterns</h3>
      <div class="metric-value" id="bronze-count">25</div>
      <div class="metric-label">Total Patterns</div>
      <div class="health-avg" id="bronze-health-avg">Loading...</div>
    </div>
  </div>

  <div class="chart-container">
    <canvas id="health-trends-chart"></canvas>
  </div>

  <div class="patterns-grid" id="patterns-grid">
    <!-- Patterns will be dynamically loaded here -->
  </div>
</div>

<style>
.health-dashboard {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  flex-wrap: wrap;
  gap: 16px;
}

.dashboard-header h2 {
  margin: 0;
  color: var(--md-primary-fg-color);
}

.last-updated {
  font-size: 14px;
  color: var(--md-default-fg-color--light);
}

.filter-controls {
  display: flex;
  gap: 8px;
}

.tier-filter {
  padding: 8px 16px;
  border: 1px solid var(--md-default-fg-color--lighter);
  background: var(--md-default-bg-color);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.tier-filter:hover {
  background: var(--md-default-fg-color--lightest);
}

.tier-filter.active {
  background: var(--md-primary-fg-color);
  color: white;
  border-color: var(--md-primary-fg-color);
}

.health-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.health-card {
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
  transition: transform 0.2s;
}

.health-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.gold-card {
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
  color: #333;
}

.silver-card {
  background: linear-gradient(135deg, #C0C0C0 0%, #909090 100%);
  color: #333;
}

.bronze-card {
  background: linear-gradient(135deg, #CD7F32 0%, #8B4513 100%);
  color: white;
}

.health-card h3 {
  margin: 0 0 16px 0;
  font-size: 20px;
}

.metric-value {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 8px;
}

.metric-label {
  font-size: 14px;
  opacity: 0.8;
}

.health-avg {
  margin-top: 16px;
  font-size: 16px;
  font-weight: 500;
}

.chart-container {
  background: var(--md-default-bg-color);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 32px;
  height: 300px;
}

.patterns-grid {
  display: grid;
  gap: 16px;
}

.pattern-card {
  background: var(--md-default-bg-color);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: all 0.2s;
  cursor: pointer;
}

.pattern-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.pattern-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.pattern-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--md-primary-fg-color);
  display: flex;
  align-items: center;
  gap: 8px;
}

.pattern-tier {
  font-size: 20px;
}

.health-score {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: bold;
}

.trend-arrow {
  font-size: 20px;
}

.trend-up { color: #4CAF50; }
.trend-stable { color: #FFC107; }
.trend-down { color: #F44336; }

.pattern-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.metric-item {
  text-align: center;
}

.metric-item-label {
  font-size: 12px;
  color: var(--md-default-fg-color--light);
  margin-bottom: 4px;
}

.metric-item-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--md-primary-fg-color);
}

.health-bar-container {
  margin-bottom: 16px;
}

.health-bar-label {
  font-size: 12px;
  color: var(--md-default-fg-color--light);
  margin-bottom: 4px;
}

.health-bar {
  height: 8px;
  background: var(--md-default-fg-color--lightest);
  border-radius: 4px;
  overflow: hidden;
}

.health-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #F44336 0%, #FFC107 50%, #4CAF50 100%);
  transition: width 0.5s ease;
}

.adoption-companies {
  margin-top: 16px;
}

.adoption-label {
  font-size: 12px;
  color: var(--md-default-fg-color--light);
  margin-bottom: 8px;
}

.company-logos {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.company-logo {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: var(--md-default-fg-color--lightest);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: var(--md-default-fg-color--light);
}

.loading {
  text-align: center;
  padding: 48px;
  color: var(--md-default-fg-color--light);
}

.error {
  text-align: center;
  padding: 48px;
  color: #F44336;
}

/* Dark mode adjustments */
[data-md-color-scheme="slate"] .health-card {
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

[data-md-color-scheme="slate"] .pattern-card {
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

[data-md-color-scheme="slate"] .gold-card,
[data-md-color-scheme="slate"] .silver-card {
  color: #333;
}

/* Responsive design */
@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-controls {
    width: 100%;
    overflow-x: auto;
  }
  
  .health-summary {
    grid-template-columns: 1fr;
  }
  
  .pattern-metrics {
    grid-template-columns: 1fr 1fr;
  }
}
</style>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
/ Pattern Health Dashboard JavaScript
(function() {
  let healthData = null;
  let trendsChart = null;
  let currentFilter = 'all';

  / Initialize dashboard
  document.addEventListener('DOMContentLoaded', function() {
    loadHealthData();
    setupFilters();
    setupAutoRefresh();
  });

  / Load health data from JSON
  async function loadHealthData() {
    try {
      const response = await fetch('/DStudio/data/health-data/pattern-health-metrics.json');
      if (!response.ok) throw new Error('Failed to load health data');
      
      healthData = await response.json();
      updateDashboard();
    } catch (error) {
      console.error('Error loading health data:', error);
      showError('Failed to load pattern health data. Please try again later.');
    }
  }

  / Update entire dashboard
  function updateDashboard() {
    if (!healthData) return;
    
    updateLastUpdated();
    updateSummaryCards();
    updateTrendsChart();
    updatePatternsGrid();
  }

  / Update last updated time
  function updateLastUpdated() {
    const element = document.getElementById('last-updated-time');
    const date = new Date(healthData.lastUpdated);
    element.textContent = date.toLocaleString();
  }

  / Update summary cards
  function updateSummaryCards() {
    const tiers = ['gold', 'silver', 'bronze'];
    
    tiers.forEach(tier => {
      const patterns = healthData.patterns.filter(p => p.tier === tier);
      const avgHealth = patterns.reduce((sum, p) => sum + p.healthScore, 0) / patterns.length;
      
      document.getElementById(`${tier}-health-avg`).textContent = 
        `Avg Health: ${avgHealth.toFixed(1)}%`;
    });
  }

  / Update trends chart
  function updateTrendsChart() {
    const ctx = document.getElementById('health-trends-chart').getContext('2d');
    
    if (trendsChart) {
      trendsChart.destroy();
    }
    
    const filteredPatterns = filterPatterns(healthData.patterns);
    const topPatterns = filteredPatterns
      .sort((a, b) => b.healthScore - a.healthScore)
      .slice(0, 10);
    
    trendsChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: healthData.trendDates,
        datasets: topPatterns.map((pattern, index) => ({
          label: pattern.name,
          data: pattern.trendData,
          borderColor: getColorForIndex(index),
          backgroundColor: getColorForIndex(index, 0.1),
          tension: 0.3
        }))
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'Pattern Health Trends (Top 10)',
            font: { size: 16 }
          },
          legend: {
            position: 'bottom',
            labels: { boxWidth: 12 }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            title: {
              display: true,
              text: 'Health Score (%)'
            }
          }
        }
      }
    });
  }

  / Update patterns grid
  function updatePatternsGrid() {
    const grid = document.getElementById('patterns-grid');
    const filteredPatterns = filterPatterns(healthData.patterns);
    const sortedPatterns = filteredPatterns.sort((a, b) => b.healthScore - a.healthScore);
    
    grid.innerHTML = sortedPatterns.map(pattern => createPatternCard(pattern)).join('');
  }

  / Create pattern card HTML
  function createPatternCard(pattern) {
    const trendClass = pattern.trend === 'up' ? 'trend-up' : 
                       pattern.trend === 'down' ? 'trend-down' : 'trend-stable';
    const trendArrow = pattern.trend === 'up' ? '↑' : 
                       pattern.trend === 'down' ? '↓' : '→';
    const tierEmoji = pattern.tier === 'gold' ? '🏆' : 
                      pattern.tier === 'silver' ? '🥈' : '🥉';
    
    return `
      <div class="pattern-card" data-tier="${pattern.tier}">
        <div class="pattern-header">
          <div class="pattern-name">
            <span class="pattern-tier">${tierEmoji}</span>
            ${pattern.name}
          </div>
          <div class="health-score">
            ${pattern.healthScore}%
            <span class="trend-arrow ${trendClass}">${trendArrow}</span>
          </div>
        </div>
        
        <div class="health-bar-container">
          <div class="health-bar-label">Overall Health</div>
          <div class="health-bar">
            <div class="health-bar-fill" style="width: ${pattern.healthScore}%"></div>
          </div>
        </div>
        
        <div class="pattern-metrics">
          <div class="metric-item">
            <div class="metric-item-label">GitHub Stars</div>
            <div class="metric-item-value">${formatNumber(pattern.metrics.githubStars)}</div>
          </div>
          <div class="metric-item">
            <div class="metric-item-label">Conf Talks</div>
            <div class="metric-item-value">${pattern.metrics.conferenceTalks}</div>
          </div>
          <div class="metric-item">
            <div class="metric-item-label">Job Mentions</div>
            <div class="metric-item-value">${formatNumber(pattern.metrics.jobMentions)}</div>
          </div>
          <div class="metric-item">
            <div class="metric-item-label">Adoption</div>
            <div class="metric-item-value">${pattern.metrics.adoptionRate}%</div>
          </div>
        </div>
        
        <div class="adoption-companies">
          <div class="adoption-label">Used by:</div>
          <div class="company-logos">
            ${pattern.adoptedBy.map(company => 
              `<div class="company-logo" title="${company}">${getCompanyInitials(company)}</div>`
            ).join('')}
          </div>
        </div>
      </div>
    `;
  }

  / Filter patterns based on current filter
  function filterPatterns(patterns) {
    if (currentFilter === 'all') return patterns;
    return patterns.filter(p => p.tier === currentFilter);
  }

  / Setup filter buttons
  function setupFilters() {
    const buttons = document.querySelectorAll('.tier-filter');
    buttons.forEach(button => {
      button.addEventListener('click', function() {
        buttons.forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        currentFilter = this.dataset.tier;
        updateDashboard();
      });
    });
  }

  / Setup auto-refresh (every 5 minutes)
  function setupAutoRefresh() {
    setInterval(loadHealthData, 5 * 60 * 1000);
  }

  / Helper functions
  function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  }

  function getCompanyInitials(company) {
    return company.split(' ').map(word => word[0]).join('').toUpperCase().slice(0, 3);
  }

  function getColorForIndex(index, alpha = 1) {
    const colors = [
      '#5448C8', '#00BCD4', '#4CAF50', '#FFC107', '#F44336',
      '#9C27B0', '#3F51B5', '#009688', '#FF5722', '#795548'
    ];
    const color = colors[index % colors.length];
    if (alpha === 1) return color;
    
    / Convert hex to rgba
    const r = parseInt(color.slice(1, 3), 16);
    const g = parseInt(color.slice(3, 5), 16);
    const b = parseInt(color.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  function showError(message) {
    document.getElementById('patterns-grid').innerHTML = 
      `<div class="error">${message}</div>`;
  }
})();
</script>

## Pattern Health Methodology

### Health Score Calculation (0-100%)

The health score is a composite metric based on:

1. **Community Activity (40%)**
   - GitHub stars and contributors
   - Stack Overflow questions/answers
   - Conference talks and workshops
   
2. **Industry Adoption (30%)**
   - Number of companies using in production
   - Scale of deployments (RPS, data volume)
   - Job market mentions
   
3. **Documentation Quality (20%)**
   - Comprehensive examples
   - Clear implementation guides
   - Active maintenance
   
4. **Innovation Velocity (10%)**
   - Recent improvements
   - Tool ecosystem growth
   - Research papers

### Trend Indicators

- **↑ Growing**: Increasing adoption, active development
- **→ Stable**: Mature pattern, steady usage
- **↓ Declining**: Better alternatives emerging, legacy status

### Tier Definitions

#### 🏆 Gold Patterns
- Used by 3+ elite tech companies
- Proven at 100M+ requests/day scale
- Active ecosystem and tooling
- Clear implementation playbooks

#### 🥈 Silver Patterns
- Widely adopted with known trade-offs
- Context-dependent usage
- May be transitioning up or down

#### 🥉 Bronze Patterns
- Legacy patterns with better alternatives
- Educational value for understanding evolution
- Limited new adoptions

## Using the Dashboard

### For Architects
- Identify trending patterns for technology radar
- Compare adoption across similar patterns
- Track pattern evolution over time

### For Engineers
- Choose patterns based on health scores
- Find companies using specific patterns
- Access implementation resources

### For Managers
- Justify pattern adoption with data
- Track team's pattern maturity
- Plan training based on trends