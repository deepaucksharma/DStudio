/**
 * Pattern Library Search Interface
 * 
 * Frontend JavaScript for searching the pattern library using the generated search index.
 * This demonstrates how to use the search index files in a web interface.
 * 
 * Dependencies:
 * - patterns.json: Main pattern data
 * - inverted_index.json: Word -> pattern mappings
 * - search_suggestions.json: Auto-complete suggestions
 * - category_index.json: Category-based filtering
 */

class PatternSearchInterface {
    constructor(indexPath = './search_index/') {
        this.indexPath = indexPath;
        this.patterns = [];
        this.invertedIndex = {};
        this.categoryIndex = {};
        this.searchSuggestions = [];
        this.initialized = false;
        
        // Search configuration
        this.maxResults = 50;
        this.debounceDelay = 300;
        this.searchDebounceTimer = null;
        
        // Initialize
        this.loadSearchIndex();
    }
    
    /**
     * Load all search index files
     */
    async loadSearchIndex() {
        try {
            console.log('🔍 Loading pattern search index...');
            
            const [patterns, invertedIndex, categoryIndex, suggestions] = await Promise.all([
                fetch(`${this.indexPath}patterns.json`).then(r => r.json()),
                fetch(`${this.indexPath}inverted_index.json`).then(r => r.json()),
                fetch(`${this.indexPath}category_index.json`).then(r => r.json()),
                fetch(`${this.indexPath}search_suggestions.json`).then(r => r.json())
            ]);
            
            this.patterns = patterns;
            this.invertedIndex = invertedIndex;
            this.categoryIndex = categoryIndex;
            this.searchSuggestions = suggestions;
            
            // Create pattern lookup map
            this.patternLookup = {};
            this.patterns.forEach(pattern => {
                this.patternLookup[pattern.id] = pattern;
            });
            
            this.initialized = true;
            console.log(`✅ Loaded ${patterns.length} patterns with ${Object.keys(invertedIndex).length} search terms`);
            
        } catch (error) {
            console.error('❌ Failed to load search index:', error);
            throw error;
        }
    }
    
    /**
     * Perform search with ranking and filtering
     */
    search(query, filters = {}) {
        if (!this.initialized) {
            console.warn('Search index not initialized');
            return [];
        }
        
        if (!query || query.trim().length < 2) {
            return this.applyFilters(this.patterns, filters).slice(0, this.maxResults);
        }
        
        const results = this.performTextSearch(query, filters);
        return results.slice(0, this.maxResults);
    }
    
    /**
     * Core text search using inverted index
     */
    performTextSearch(query, filters) {
        const queryTokens = this.tokenizeQuery(query.toLowerCase());
        const patternScores = new Map();
        
        // Find matching patterns using inverted index
        for (const token of queryTokens) {
            // Exact matches
            if (this.invertedIndex[token]) {
                for (const patternId of this.invertedIndex[token]) {
                    patternScores.set(patternId, (patternScores.get(patternId) || 0) + 2.0);
                }
            }
            
            // Partial matches
            for (const [indexedTerm, patternIds] of Object.entries(this.invertedIndex)) {
                if (indexedTerm.includes(token) && indexedTerm !== token) {
                    for (const patternId of patternIds) {
                        patternScores.set(patternId, (patternScores.get(patternId) || 0) + 1.0);
                    }
                }
            }
        }
        
        // Convert to results with full pattern data
        let results = [];
        for (const [patternId, baseScore] of patternScores.entries()) {
            const pattern = this.patternLookup[patternId];
            if (pattern) {
                const finalScore = this.calculateRelevanceScore(pattern, queryTokens, baseScore);
                results.push({
                    ...pattern,
                    searchScore: finalScore,
                    matchReason: this.getMatchReason(pattern, queryTokens)
                });
            }
        }
        
        // Sort by relevance
        results.sort((a, b) => b.searchScore - a.searchScore);
        
        // Apply filters
        return this.applyFilters(results, filters);
    }
    
    /**
     * Calculate relevance score for ranking
     */
    calculateRelevanceScore(pattern, queryTokens, baseScore) {
        let score = baseScore;
        
        const title = pattern.title.toLowerCase();
        const description = pattern.description.toLowerCase();
        const queryString = queryTokens.join(' ');
        
        // Title matches (highest weight)
        if (title.includes(queryString)) score += 10;
        for (const token of queryTokens) {
            if (title.includes(token)) score += 5;
        }
        
        // Description matches
        if (description.includes(queryString)) score += 7;
        for (const token of queryTokens) {
            if (description.includes(token)) score += 3;
        }
        
        // Category/tag matches
        const categoryMatch = pattern.category.toLowerCase().includes(queryString);
        if (categoryMatch) score += 4;
        
        for (const tag of pattern.tags || []) {
            if (tag.toLowerCase().includes(queryString)) score += 3;
        }
        
        // Company matches
        for (const company of pattern.companies || []) {
            if (company.toLowerCase().includes(queryString)) score += 4;
        }
        
        // Excellence tier boost
        const tierMultiplier = {
            'gold': 1.3,
            'silver': 1.1,
            'bronze': 0.8
        };
        score *= tierMultiplier[pattern.excellence_tier] || 1.0;
        
        // Relevance boost
        const relevanceMultiplier = {
            'mainstream': 1.2,
            'growing': 1.15,
            'declining': 0.8,
            'niche': 0.9
        };
        score *= relevanceMultiplier[pattern.current_relevance] || 1.0;
        
        return score;
    }
    
    /**
     * Apply filters to search results
     */
    applyFilters(patterns, filters) {
        let filtered = patterns;
        
        // Category filter
        if (filters.category && filters.category !== 'all') {
            filtered = filtered.filter(p => p.category === filters.category);
        }
        
        // Excellence tier filter
        if (filters.tier && filters.tier !== 'all') {
            filtered = filtered.filter(p => p.excellence_tier === filters.tier);
        }
        
        // Difficulty filter
        if (filters.difficulty && filters.difficulty !== 'all') {
            filtered = filtered.filter(p => p.difficulty === filters.difficulty);
        }
        
        // Status filter
        if (filters.status && filters.status !== 'all') {
            filtered = filtered.filter(p => p.pattern_status === filters.status);
        }
        
        // Company filter
        if (filters.company) {
            filtered = filtered.filter(p => 
                p.companies.some(c => c.toLowerCase().includes(filters.company.toLowerCase()))
            );
        }
        
        // Tag filter
        if (filters.tag) {
            filtered = filtered.filter(p =>
                p.tags.some(t => t.toLowerCase().includes(filters.tag.toLowerCase()))
            );
        }
        
        return filtered;
    }
    
    /**
     * Get search suggestions for autocomplete
     */
    getSuggestions(query, limit = 10) {
        if (!query || query.length < 2) {
            return this.searchSuggestions.slice(0, limit);
        }
        
        const queryLower = query.toLowerCase();
        const suggestions = [];
        
        // Match against suggestion list
        for (const suggestion of this.searchSuggestions) {
            if (suggestion.query.toLowerCase().includes(queryLower)) {
                suggestions.push(suggestion);
            }
        }
        
        // Add pattern titles that match
        for (const pattern of this.patterns) {
            if (pattern.title.toLowerCase().includes(queryLower) && 
                !suggestions.some(s => s.query === pattern.title)) {
                suggestions.push({
                    query: pattern.title,
                    pattern_count: 1,
                    category: 'pattern'
                });
            }
        }
        
        return suggestions.slice(0, limit);
    }
    
    /**
     * Get patterns by category
     */
    getPatternsByCategory(category) {
        const patternIds = this.categoryIndex[category] || [];
        return patternIds.map(id => this.patternLookup[id]).filter(Boolean);
    }
    
    /**
     * Get related patterns based on tags and category
     */
    getRelatedPatterns(pattern, limit = 5) {
        const related = new Set();
        
        // Same category patterns
        const categoryPatterns = this.getPatternsByCategory(pattern.category);
        categoryPatterns.forEach(p => {
            if (p.id !== pattern.id) related.add(p);
        });
        
        // Same tag patterns
        for (const tag of pattern.tags || []) {
            for (const p of this.patterns) {
                if (p.id !== pattern.id && p.tags.includes(tag)) {
                    related.add(p);
                }
            }
        }
        
        // Same company patterns
        for (const company of pattern.companies || []) {
            for (const p of this.patterns) {
                if (p.id !== pattern.id && p.companies.includes(company)) {
                    related.add(p);
                }
            }
        }
        
        return Array.from(related)
            .sort((a, b) => {
                // Prefer same tier
                if (a.excellence_tier === pattern.excellence_tier && 
                    b.excellence_tier !== pattern.excellence_tier) return -1;
                if (b.excellence_tier === pattern.excellence_tier && 
                    a.excellence_tier !== pattern.excellence_tier) return 1;
                return 0;
            })
            .slice(0, limit);
    }
    
    /**
     * Tokenize search query
     */
    tokenizeQuery(query) {
        return query.toLowerCase()
            .replace(/[^\w\s-]/g, ' ')
            .split(/\s+/)
            .filter(token => token.length > 2);
    }
    
    /**
     * Get human-readable match reason
     */
    getMatchReason(pattern, queryTokens) {
        const reasons = [];
        const query = queryTokens.join(' ');
        
        if (pattern.title.toLowerCase().includes(query)) {
            reasons.push('Title match');
        } else if (queryTokens.some(token => pattern.title.toLowerCase().includes(token))) {
            reasons.push('Title keyword');
        }
        
        if (pattern.description.toLowerCase().includes(query)) {
            reasons.push('Description match');
        }
        
        if (pattern.category.toLowerCase().includes(query)) {
            reasons.push('Category');
        }
        
        const tagMatches = (pattern.tags || []).filter(tag => 
            queryTokens.some(token => tag.toLowerCase().includes(token))
        );
        if (tagMatches.length > 0) {
            reasons.push(`Tag: ${tagMatches[0]}`);
        }
        
        const companyMatches = (pattern.companies || []).filter(company =>
            queryTokens.some(token => company.toLowerCase().includes(token))
        );
        if (companyMatches.length > 0) {
            reasons.push(`Used by ${companyMatches[0]}`);
        }
        
        return reasons.length > 0 ? reasons.join(', ') : 'Content match';
    }
    
    /**
     * Get search analytics
     */
    getSearchAnalytics() {
        return {
            totalPatterns: this.patterns.length,
            categories: Object.keys(this.categoryIndex).length,
            searchTerms: Object.keys(this.invertedIndex).length,
            suggestions: this.searchSuggestions.length,
            
            patternsByTier: this.patterns.reduce((acc, pattern) => {
                acc[pattern.excellence_tier] = (acc[pattern.excellence_tier] || 0) + 1;
                return acc;
            }, {}),
            
            patternsByCategory: this.patterns.reduce((acc, pattern) => {
                acc[pattern.category] = (acc[pattern.category] || 0) + 1;
                return acc;
            }, {})
        };
    }
}

/**
 * Example usage in HTML/DOM
 */
class PatternSearchUI {
    constructor(containerSelector, indexPath = './search_index/') {
        this.container = document.querySelector(containerSelector);
        this.searchInterface = new PatternSearchInterface(indexPath);
        this.currentResults = [];
        
        this.init();
    }
    
    async init() {
        await this.searchInterface.loadSearchIndex();
        this.setupUI();
        this.bindEvents();
    }
    
    setupUI() {
        this.container.innerHTML = `
            <div class="pattern-search-container">
                <div class="search-header">
                    <h2>Pattern Library Search</h2>
                    <div class="search-stats" id="search-stats"></div>
                </div>
                
                <div class="search-input-container">
                    <input type="text" id="pattern-search" 
                           placeholder="Search patterns... (try: circuit breaker, netflix, microservices)"
                           autocomplete="off">
                    <div class="search-suggestions" id="search-suggestions"></div>
                </div>
                
                <div class="search-filters">
                    <select id="category-filter">
                        <option value="all">All Categories</option>
                    </select>
                    <select id="tier-filter">
                        <option value="all">All Tiers</option>
                        <option value="gold">🥇 Gold</option>
                        <option value="silver">🥈 Silver</option>
                        <option value="bronze">🥉 Bronze</option>
                    </select>
                    <select id="difficulty-filter">
                        <option value="all">All Difficulties</option>
                        <option value="beginner">Beginner</option>
                        <option value="intermediate">Intermediate</option>
                        <option value="advanced">Advanced</option>
                    </select>
                    <button id="clear-filters">Clear Filters</button>
                </div>
                
                <div class="search-results" id="search-results">
                    <div class="loading">Loading patterns...</div>
                </div>
            </div>
        `;
        
        this.populateFilters();
        this.updateSearchStats();
        this.displayInitialResults();
    }
    
    populateFilters() {
        const categoryFilter = document.getElementById('category-filter');
        const categories = Object.keys(this.searchInterface.categoryIndex);
        
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
            categoryFilter.appendChild(option);
        });
    }
    
    bindEvents() {
        const searchInput = document.getElementById('pattern-search');
        const categoryFilter = document.getElementById('category-filter');
        const tierFilter = document.getElementById('tier-filter');
        const difficultyFilter = document.getElementById('difficulty-filter');
        const clearFilters = document.getElementById('clear-filters');
        
        // Search input with debouncing
        searchInput.addEventListener('input', (e) => {
            clearTimeout(this.searchDebounceTimer);
            this.searchDebounceTimer = setTimeout(() => {
                this.performSearch(e.target.value);
            }, 300);
        });
        
        // Search suggestions
        searchInput.addEventListener('focus', () => this.showSuggestions());
        searchInput.addEventListener('blur', () => setTimeout(() => this.hideSuggestions(), 150));
        
        // Filters
        [categoryFilter, tierFilter, difficultyFilter].forEach(filter => {
            filter.addEventListener('change', () => this.performSearch());
        });
        
        // Clear filters
        clearFilters.addEventListener('click', () => {
            searchInput.value = '';
            categoryFilter.value = 'all';
            tierFilter.value = 'all';
            difficultyFilter.value = 'all';
            this.performSearch();
        });
    }
    
    performSearch(query = null) {
        if (query === null) {
            query = document.getElementById('pattern-search').value;
        }
        
        const filters = {
            category: document.getElementById('category-filter').value,
            tier: document.getElementById('tier-filter').value,
            difficulty: document.getElementById('difficulty-filter').value
        };
        
        this.currentResults = this.searchInterface.search(query, filters);
        this.displayResults(this.currentResults);
        this.updateSearchStats(query, this.currentResults.length);
    }
    
    displayResults(results) {
        const container = document.getElementById('search-results');
        
        if (results.length === 0) {
            container.innerHTML = `
                <div class="no-results">
                    <h3>No patterns found</h3>
                    <p>Try different search terms or adjust your filters.</p>
                </div>
            `;
            return;
        }
        
        const html = results.map(pattern => `
            <div class="pattern-card tier-${pattern.excellence_tier}">
                <div class="pattern-header">
                    <h3>
                        <a href="${pattern.url}">${pattern.title}</a>
                        <span class="tier-badge ${pattern.excellence_tier}">${pattern.excellence_tier.toUpperCase()}</span>
                    </h3>
                    ${pattern.searchScore ? `<div class="match-info">${pattern.matchReason}</div>` : ''}
                </div>
                <p class="pattern-description">${pattern.description}</p>
                <div class="pattern-meta">
                    <span class="category">${pattern.category}</span>
                    <span class="difficulty">${pattern.difficulty}</span>
                    ${pattern.companies.length > 0 ? `<span class="companies">${pattern.companies.slice(0, 3).join(', ')}</span>` : ''}
                </div>
                <div class="pattern-tags">
                    ${pattern.tags.slice(0, 5).map(tag => `<span class="tag">#${tag}</span>`).join('')}
                </div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }
    
    displayInitialResults() {
        // Show top gold patterns initially
        const goldPatterns = this.searchInterface.patterns
            .filter(p => p.excellence_tier === 'gold')
            .sort((a, b) => b.word_count - a.word_count)
            .slice(0, 20);
            
        this.displayResults(goldPatterns);
    }
    
    showSuggestions() {
        const input = document.getElementById('pattern-search');
        const suggestions = this.searchInterface.getSuggestions(input.value);
        const container = document.getElementById('search-suggestions');
        
        if (suggestions.length === 0) {
            container.style.display = 'none';
            return;
        }
        
        const html = suggestions.map(suggestion => `
            <div class="suggestion" data-query="${suggestion.query}">
                <span class="query">${suggestion.query}</span>
                <span class="count">${suggestion.pattern_count} patterns</span>
                <span class="category">${suggestion.category}</span>
            </div>
        `).join('');
        
        container.innerHTML = html;
        container.style.display = 'block';
        
        // Bind suggestion clicks
        container.querySelectorAll('.suggestion').forEach(el => {
            el.addEventListener('click', () => {
                input.value = el.dataset.query;
                this.performSearch(el.dataset.query);
                container.style.display = 'none';
            });
        });
    }
    
    hideSuggestions() {
        document.getElementById('search-suggestions').style.display = 'none';
    }
    
    updateSearchStats(query = '', resultCount = null) {
        const analytics = this.searchInterface.getSearchAnalytics();
        const statsEl = document.getElementById('search-stats');
        
        if (resultCount !== null) {
            statsEl.innerHTML = `
                Found ${resultCount} patterns for "${query}" 
                (${analytics.totalPatterns} total patterns)
            `;
        } else {
            statsEl.innerHTML = `
                ${analytics.totalPatterns} patterns • 
                ${analytics.categories} categories • 
                ${analytics.searchTerms} search terms
            `;
        }
    }
}

// Example initialization
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('pattern-search-app')) {
        new PatternSearchUI('#pattern-search-app');
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { PatternSearchInterface, PatternSearchUI };
}