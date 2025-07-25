// Pattern Relationship Explorer Interactive Features

document.addEventListener('DOMContentLoaded', function() {
    // Initialize pattern relationship interactions
    initializePatternExplorer();
});

function initializePatternExplorer() {
    // Add interactive tooltips to pattern relationships
    addPatternTooltips();
    
    // Enable pattern search functionality
    enablePatternSearch();
    
    // Add interactive pattern filtering
    addPatternFiltering();
    
    // Initialize pattern complexity visualizations
    initializeComplexityMeters();
}

// Add tooltips showing pattern relationships
function addPatternTooltips() {
    const patternCards = document.querySelectorAll('.pattern-card');
    
    patternCards.forEach(card => {
        card.addEventListener('mouseenter', function(e) {
            const patternName = this.dataset.pattern;
            const relatedPatterns = getRelatedPatterns(patternName);
            showTooltip(e, relatedPatterns);
        });
        
        card.addEventListener('mouseleave', function() {
            hideTooltip();
        });
    });
}

// Get related patterns for a given pattern
function getRelatedPatterns(patternName) {
    const relationships = {
        'Circuit Breaker': ['Retry', 'Timeout', 'Bulkhead', 'Fallback'],
        'Event Sourcing': ['CQRS', 'Saga', 'Event Store', 'Snapshots'],
        'Microservices': ['API Gateway', 'Service Discovery', 'Service Mesh', 'Saga'],
        'Sharding': ['Consistent Hashing', 'Rebalancing', 'Partition Key'],
        'CQRS': ['Event Sourcing', 'Read Replicas', 'Caching'],
        'Service Mesh': ['Circuit Breaker', 'Load Balancing', 'Observability'],
        'Saga': ['Compensating Transactions', 'Event Sourcing', 'Distributed Lock'],
        'API Gateway': ['Rate Limiting', 'Authentication', 'Caching']
    };
    
    return relationships[patternName] || [];
}

// Show tooltip with related patterns
function showTooltip(event, patterns) {
    const tooltip = document.createElement('div');
    tooltip.className = 'relationship-tooltip visible';
    tooltip.innerHTML = `
        <strong>Related Patterns:</strong><br>
        ${patterns.join(', ')}
    `;
    
    tooltip.style.left = event.pageX + 10 + 'px';
    tooltip.style.top = event.pageY + 10 + 'px';
    
    document.body.appendChild(tooltip);
}

// Hide tooltip
function hideTooltip() {
    const tooltips = document.querySelectorAll('.relationship-tooltip');
    tooltips.forEach(tooltip => tooltip.remove());
}

// Enable pattern search with highlighting
function enablePatternSearch() {
    const searchInput = document.querySelector('#pattern-search');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const patterns = document.querySelectorAll('.pattern-card, .pattern-search-result');
        
        patterns.forEach(pattern => {
            const patternText = pattern.textContent.toLowerCase();
            if (patternText.includes(searchTerm)) {
                pattern.style.display = 'block';
                highlightSearchTerm(pattern, searchTerm);
            } else {
                pattern.style.display = 'none';
            }
        });
        
        updateSearchResults(searchTerm);
    });
}

// Highlight search terms in pattern cards
function highlightSearchTerm(element, term) {
    if (!term) {
        element.innerHTML = element.textContent;
        return;
    }
    
    const regex = new RegExp(`(${term})`, 'gi');
    element.innerHTML = element.textContent.replace(regex, '<mark>$1</mark>');
}

// Update search results with relevance
function updateSearchResults(searchTerm) {
    const resultsContainer = document.querySelector('#search-results');
    if (!resultsContainer) return;
    
    // Clear previous results
    resultsContainer.innerHTML = '';
    
    if (!searchTerm) return;
    
    // Find matching patterns
    const patterns = findMatchingPatterns(searchTerm);
    
    // Display results with relevance
    patterns.forEach(pattern => {
        const resultDiv = createSearchResult(pattern);
        resultsContainer.appendChild(resultDiv);
    });
}

// Create search result element
function createSearchResult(pattern) {
    const div = document.createElement('div');
    div.className = 'pattern-search-result';
    
    div.innerHTML = `
        <div>
            <strong>${pattern.name}</strong>
            <span class="pattern-category ${pattern.category}">${pattern.category}</span>
        </div>
        <div class="pattern-relevance">
            ${createRelevanceDots(pattern.relevance)}
        </div>
    `;
    
    div.addEventListener('click', () => {
        navigateToPattern(pattern.name);
    });
    
    return div;
}

// Create relevance indicator dots
function createRelevanceDots(relevance) {
    let dots = '';
    for (let i = 0; i < 5; i++) {
        dots += `<span class="relevance-dot ${i < relevance ? 'filled' : ''}"></span>`;
    }
    return dots;
}

// Add pattern filtering by category
function addPatternFiltering() {
    const filterButtons = document.querySelectorAll('.filter-button');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const category = this.dataset.category;
            filterPatternsByCategory(category);
            
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

// Filter patterns by category
function filterPatternsByCategory(category) {
    const patterns = document.querySelectorAll('.pattern-card');
    
    patterns.forEach(pattern => {
        if (category === 'all' || pattern.dataset.category === category) {
            pattern.style.display = 'block';
            pattern.style.opacity = '1';
        } else {
            pattern.style.opacity = '0.3';
        }
    });
}

// Initialize complexity meters with animations
function initializeComplexityMeters() {
    const meters = document.querySelectorAll('.complexity-meter');
    
    // Use Intersection Observer for animation on scroll
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateComplexityMeter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    });
    
    meters.forEach(meter => observer.observe(meter));
}

// Animate complexity meter fill
function animateComplexityMeter(meter) {
    const fill = meter.querySelector('.complexity-fill');
    const complexity = meter.dataset.complexity;
    
    setTimeout(() => {
        fill.style.width = `${complexity}%`;
    }, 100);
}

// Navigate to pattern page
function navigateToPattern(patternName) {
    const patternSlug = patternName.toLowerCase().replace(/\s+/g, '-');
    window.location.href = `/patterns/${patternSlug}/`;
}

// Find matching patterns based on search term
function findMatchingPatterns(searchTerm) {
    // This would typically fetch from a data source
    const allPatterns = [
        { name: 'Circuit Breaker', category: 'resilience', relevance: 5 },
        { name: 'Event Sourcing', category: 'data', relevance: 4 },
        { name: 'Service Mesh', category: 'communication', relevance: 4 },
        { name: 'Saga Pattern', category: 'coordination', relevance: 3 },
        { name: 'CQRS', category: 'data', relevance: 4 }
    ];
    
    return allPatterns.filter(pattern => 
        pattern.name.toLowerCase().includes(searchTerm)
    ).sort((a, b) => b.relevance - a.relevance);
}

// Add interactive pattern relationship visualization
function initializeRelationshipGraph() {
    const canvas = document.querySelector('#relationship-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const patterns = getPatternNodes();
    const connections = getPatternConnections();
    
    // Draw connections
    connections.forEach(connection => {
        drawConnection(ctx, connection);
    });
    
    // Draw pattern nodes
    patterns.forEach(pattern => {
        drawPatternNode(ctx, pattern);
    });
    
    // Add interactivity
    canvas.addEventListener('click', handleCanvasClick);
    canvas.addEventListener('mousemove', handleCanvasHover);
}

// Export functions for use in other scripts
window.PatternExplorer = {
    initialize: initializePatternExplorer,
    filterByCategory: filterPatternsByCategory,
    search: enablePatternSearch
};