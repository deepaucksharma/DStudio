---
title: Pattern Discovery Tool
description: Find the perfect distributed systems patterns for your specific needs
hide:
  - toc
---

# 🔍 Pattern Discovery Tool

**Find the perfect patterns for your distributed systems challenges in seconds.**

<div class="pattern-filter-container">
    <div class="filter-section">
        <h3>🎯 Filter by Excellence Tier</h3>
        <div class="tier-filters">
            <button class="filter-chip tier-gold active" data-tier="gold">
                🥇 Gold (38)
                <span class="description">Battle-tested at scale</span>
            </button>
            <button class="filter-chip tier-silver active" data-tier="silver">
                🥈 Silver (38)
                <span class="description">Production-ready</span>
            </button>
            <button class="filter-chip tier-bronze" data-tier="bronze">
                🥉 Bronze (25)
                <span class="description">Legacy/Migrating</span>
            </button>
        </div>
    </div>

    <div class="filter-section">
        <h3>🔧 Filter by Problem Domain</h3>
        <div class="domain-filters">
            <button class="filter-chip" data-domain="communication">
                📡 Service Communication
            </button>
            <button class="filter-chip" data-domain="data">
                💾 Data Management
            </button>
            <button class="filter-chip" data-domain="resilience">
                🛡️ Resilience & Reliability
            </button>
            <button class="filter-chip" data-domain="performance">
                ⚡ Performance & Scale
            </button>
            <button class="filter-chip" data-domain="operations">
                🔧 Operations
            </button>
        </div>
    </div>

    <div class="filter-section">
        <h3>📏 Filter by Scale</h3>
        <div class="scale-filters">
            <button class="filter-chip" data-scale="startup">
                🌱 Startup (<10K users)
            </button>
            <button class="filter-chip" data-scale="growth">
                📈 Growth (10K-100K)
            </button>
            <button class="filter-chip" data-scale="enterprise">
                🏢 Enterprise (100K-1M)
            </button>
            <button class="filter-chip" data-scale="hyperscale">
                🚀 Hyperscale (>1M)
            </button>
        </div>
    </div>

    <div class="search-section">
        <input type="text" id="pattern-search" placeholder="🔍 Search patterns by name or keyword..." />
    </div>
</div>

## 📊 Quick Pattern Selector

<div class="quick-selector">
    <h3>I need patterns for...</h3>
    <div class="quick-options">
        <a href="#" class="quick-option" data-filter="high-availability">
            🎯 High Availability System
            <span>Circuit Breaker • Failover • Health Checks</span>
        </a>
        <a href="#" class="quick-option" data-filter="real-time">
            ⚡ Real-time Processing
            <span>Event Streaming • WebSocket • Pub-Sub</span>
        </a>
        <a href="#" class="quick-option" data-filter="microservices">
            🔗 Microservices Architecture
            <span>API Gateway • Service Mesh • Saga</span>
        </a>
        <a href="#" class="quick-option" data-filter="data-consistency">
            💾 Data Consistency
            <span>Event Sourcing • CQRS • Distributed Lock</span>
        </a>
        <a href="#" class="quick-option" data-filter="global-scale">
            🌍 Global Scale
            <span>Multi-region • CDN • Geo-sharding</span>
        </a>
        <a href="#" class="quick-option" data-filter="cost-optimization">
            💰 Cost Optimization
            <span>Caching • Compression • Serverless</span>
        </a>
    </div>
</div>

## 🏆 Pattern Results

<div id="pattern-results" class="pattern-grid">
    <!-- Gold Patterns Section -->
    <div class="tier-section gold-section">
        <h3>🥇 Gold Patterns - Battle-tested Excellence</h3>
        <div class="pattern-cards">
            <!-- Patterns will be dynamically loaded here -->
            <div class="pattern-card gold">
                <h4><a href="../../patterns/circuit-breaker/">Circuit Breaker</a></h4>
                <p>Prevent cascade failures in distributed systems</p>
                <div class="pattern-meta">
                    <span class="tag">Resilience</span>
                    <span class="tag">All Scales</span>
                    <span class="success-rate">95% Success</span>
                </div>
                <div class="pattern-examples">
                    <strong>Used by:</strong> Netflix (100B req/day), Amazon, Uber
                </div>
            </div>
            <!-- More pattern cards... -->
        </div>
    </div>

    <!-- Silver Patterns Section -->
    <div class="tier-section silver-section">
        <h3>🥈 Silver Patterns - Specialized Excellence</h3>
        <div class="pattern-cards">
            <!-- Silver patterns... -->
        </div>
    </div>

    <!-- Bronze Patterns Section -->
    <div class="tier-section bronze-section">
        <h3>🥉 Bronze Patterns - Legacy & Migration Targets</h3>
        <div class="pattern-cards">
            <!-- Bronze patterns... -->
        </div>
    </div>
</div>

## 🎯 Pattern Selection Wizard

<div class="wizard-container" id="pattern-wizard">
    <h3>Answer 3 questions to get personalized recommendations:</h3>
    
    <div class="wizard-step active" data-step="1">
        <h4>1. What's your primary challenge?</h4>
        <div class="wizard-options">
            <button data-value="reliability">System keeps failing</button>
            <button data-value="performance">Too slow/can't scale</button>
            <button data-value="consistency">Data inconsistencies</button>
            <button data-value="complexity">Too complex to manage</button>
        </div>
    </div>

    <div class="wizard-step" data-step="2">
        <h4>2. What's your scale?</h4>
        <div class="wizard-options">
            <button data-value="small">< 10K users</button>
            <button data-value="medium">10K - 100K users</button>
            <button data-value="large">100K - 1M users</button>
            <button data-value="xlarge">> 1M users</button>
        </div>
    </div>

    <div class="wizard-step" data-step="3">
        <h4>3. What's your constraint?</h4>
        <div class="wizard-options">
            <button data-value="consistency">Must be consistent</button>
            <button data-value="availability">Can't have downtime</button>
            <button data-value="performance">Must be fast</button>
            <button data-value="cost">Must be cost-effective</button>
        </div>
    </div>

    <div class="wizard-results" style="display: none;">
        <h4>🎯 Recommended Patterns for You:</h4>
        <div id="wizard-recommendations"></div>
    </div>
</div>

## 📊 Pattern Comparison Tool

<div class="comparison-prompt">
    <h3>Compare Similar Patterns</h3>
    <div class="comparison-options">
        <a href="../comparisons/caching-patterns-comparison/" class="comparison-link">
            💾 Compare Caching Patterns
            <span>Cache-aside vs Read-through vs Write-through</span>
        </a>
        <a href="../comparisons/messaging-patterns-comparison/" class="comparison-link">
            📨 Compare Messaging Patterns
            <span>Queue vs Pub-Sub vs Event Streaming</span>
        </a>
        <a href="../comparisons/consistency-patterns-comparison/" class="comparison-link">
            🔄 Compare Consistency Patterns
            <span>2PC vs Saga vs Event Sourcing</span>
        </a>
        <a href="../comparisons/resilience-patterns-comparison/" class="comparison-link">
            🛡️ Compare Resilience Patterns
            <span>Circuit Breaker vs Retry vs Timeout</span>
        </a>
    </div>
</div>

## 🚀 Next Steps

<div class="next-steps">
    <div class="step">
        <h4>1. Explore Pattern Details</h4>
        <p>Click any pattern to see implementation guides, examples, and trade-offs</p>
    </div>
    <div class="step">
        <h4>2. Check Case Studies</h4>
        <p>See how top companies implement these patterns in production</p>
    </div>
    <div class="step">
        <h4>3. Plan Implementation</h4>
        <p>Use our implementation calculator to estimate effort and timeline</p>
    </div>
</div>

---

<div class="navigation-links">
    <a href="gold-patterns/" class="nav-card gold">
        <h3>🥇 Explore Gold Patterns</h3>
        <p>Deep dive into battle-tested patterns</p>
    </a>
    <a href="silver-patterns/" class="nav-card silver">
        <h3>🥈 Explore Silver Patterns</h3>
        <p>Specialized patterns for specific needs</p>
    </a>
    <a href="bronze-patterns/" class="nav-card bronze">
        <h3>🥉 Migration from Bronze</h3>
        <p>Upgrade paths from legacy patterns</p>
    </a>
</div>

<script>
// Pattern discovery interactivity
document.addEventListener('DOMContentLoaded', function() {
    // Filter functionality
    const filterChips = document.querySelectorAll('.filter-chip');
    const patternCards = document.querySelectorAll('.pattern-card');
    
    filterChips.forEach(chip => {
        chip.addEventListener('click', function() {
            this.classList.toggle('active');
            applyFilters();
        });
    });

    // Search functionality
    const searchInput = document.getElementById('pattern-search');
    searchInput.addEventListener('input', function() {
        applyFilters();
    });

    // Quick selector
    const quickOptions = document.querySelectorAll('.quick-option');
    quickOptions.forEach(option => {
        option.addEventListener('click', function(e) {
            e.preventDefault();
            // Apply predefined filters
            const filterSet = this.dataset.filter;
            applyQuickFilter(filterSet);
        });
    });

    // Pattern wizard
    const wizardOptions = document.querySelectorAll('.wizard-options button');
    wizardOptions.forEach(button => {
        button.addEventListener('click', function() {
            const step = this.closest('.wizard-step');
            const nextStep = step.nextElementSibling;
            
            // Store answer
            const stepNum = step.dataset.step;
            storeWizardAnswer(stepNum, this.dataset.value);
            
            // Move to next step or show results
            step.classList.remove('active');
            if (nextStep && nextStep.classList.contains('wizard-step')) {
                nextStep.classList.add('active');
            } else {
                showWizardResults();
            }
        });
    });

    function applyFilters() {
        // Implementation for filtering patterns
        console.log('Applying filters...');
    }

    function applyQuickFilter(filterSet) {
        // Implementation for quick filters
        console.log('Applying quick filter:', filterSet);
    }

    function storeWizardAnswer(step, value) {
        // Store wizard answers
        sessionStorage.setItem(`wizard_step_${step}`, value);
    }

    function showWizardResults() {
        // Show personalized recommendations
        document.querySelector('.wizard-results').style.display = 'block';
    }
});
</script>

<style>
.pattern-filter-container {
    background: var(--md-code-bg-color);
    padding: 2rem;
    border-radius: 0.5rem;
    margin-bottom: 2rem;
}

.filter-section {
    margin-bottom: 1.5rem;
}

.filter-section h3 {
    margin-top: 0;
    margin-bottom: 1rem;
}

.tier-filters, .domain-filters, .scale-filters {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.filter-chip {
    padding: 0.5rem 1rem;
    border: 1px solid var(--md-default-fg-color--light);
    background: var(--md-default-bg-color);
    border-radius: 2rem;
    cursor: pointer;
    transition: all 0.3s;
}

.filter-chip:hover {
    border-color: var(--md-accent-fg-color);
}

.filter-chip.active {
    background: var(--md-accent-bg-color);
    color: var(--md-accent-fg-color);
    border-color: var(--md-accent-fg-color);
}

.filter-chip .description {
    display: block;
    font-size: 0.8rem;
    opacity: 0.8;
}

.tier-gold { border-color: #FFD700; }
.tier-gold.active { background: #FFD700; color: #000; }

.tier-silver { border-color: #C0C0C0; }
.tier-silver.active { background: #C0C0C0; color: #000; }

.tier-bronze { border-color: #CD7F32; }
.tier-bronze.active { background: #CD7F32; color: #FFF; }

.search-section {
    margin-top: 1rem;
}

#pattern-search {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 1px solid var(--md-default-fg-color--light);
    border-radius: 0.25rem;
    background: var(--md-default-bg-color);
    font-size: 1rem;
}

.quick-selector {
    background: var(--md-default-bg-color);
    padding: 2rem;
    border-radius: 0.5rem;
    margin: 2rem 0;
}

.quick-options {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.quick-option {
    padding: 1rem;
    border: 1px solid var(--md-default-fg-color--light);
    border-radius: 0.25rem;
    text-decoration: none;
    color: inherit;
    display: block;
    transition: all 0.3s;
}

.quick-option:hover {
    border-color: var(--md-accent-fg-color);
    transform: translateY(-2px);
}

.quick-option span {
    display: block;
    font-size: 0.9rem;
    color: var(--md-default-fg-color--light);
    margin-top: 0.5rem;
}

.pattern-grid {
    margin: 2rem 0;
}

.tier-section {
    margin-bottom: 3rem;
}

.pattern-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-top: 1rem;
}

.pattern-card {
    padding: 1.5rem;
    border: 1px solid var(--md-default-fg-color--light);
    border-radius: 0.5rem;
    transition: all 0.3s;
}

.pattern-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.pattern-card.gold {
    border-left: 4px solid #FFD700;
}

.pattern-card.silver {
    border-left: 4px solid #C0C0C0;
}

.pattern-card.bronze {
    border-left: 4px solid #CD7F32;
}

.pattern-meta {
    margin: 1rem 0;
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.tag {
    padding: 0.25rem 0.5rem;
    background: var(--md-code-bg-color);
    border-radius: 0.25rem;
    font-size: 0.85rem;
}

.success-rate {
    padding: 0.25rem 0.5rem;
    background: #4CAF50;
    color: white;
    border-radius: 0.25rem;
    font-size: 0.85rem;
}

.pattern-examples {
    margin-top: 1rem;
    font-size: 0.9rem;
    color: var(--md-default-fg-color--light);
}

.wizard-container {
    background: var(--md-code-bg-color);
    padding: 2rem;
    border-radius: 0.5rem;
    margin: 2rem 0;
}

.wizard-step {
    display: none;
}

.wizard-step.active {
    display: block;
}

.wizard-options {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.wizard-options button {
    padding: 1rem;
    border: 1px solid var(--md-default-fg-color--light);
    background: var(--md-default-bg-color);
    border-radius: 0.25rem;
    cursor: pointer;
    transition: all 0.3s;
}

.wizard-options button:hover {
    border-color: var(--md-accent-fg-color);
    background: var(--md-accent-bg-color);
}

.comparison-prompt {
    margin: 2rem 0;
}

.comparison-options {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.comparison-link {
    padding: 1rem;
    border: 1px solid var(--md-default-fg-color--light);
    border-radius: 0.25rem;
    text-decoration: none;
    color: inherit;
    display: block;
    transition: all 0.3s;
}

.comparison-link:hover {
    border-color: var(--md-accent-fg-color);
    transform: translateY(-2px);
}

.comparison-link span {
    display: block;
    font-size: 0.9rem;
    color: var(--md-default-fg-color--light);
    margin-top: 0.5rem;
}

.next-steps {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2rem;
    margin: 2rem 0;
    text-align: center;
}

.navigation-links {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}

.nav-card {
    padding: 1.5rem;
    border-radius: 0.5rem;
    text-decoration: none;
    color: inherit;
    transition: all 0.3s;
}

.nav-card:hover {
    transform: translateY(-2px);
}

.nav-card.gold {
    background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
    color: #000;
}

.nav-card.silver {
    background: linear-gradient(135deg, #C0C0C0 0%, #808080 100%);
    color: #000;
}

.nav-card.bronze {
    background: linear-gradient(135deg, #CD7F32 0%, #8B4513 100%);
    color: #FFF;
}
</style>