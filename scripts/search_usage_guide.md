# Pattern Library Search Index Usage Guide

This guide shows how to use the comprehensive search index for the pattern library to build powerful search experiences.

## 📁 Generated Files Overview

The search index builder creates the following files in `/search_index/`:

| File | Purpose | Size | Usage |
|------|---------|------|-------|
| `patterns.json` | Complete pattern data with metadata | ~590KB | Main data source |
| `inverted_index.json` | Word → pattern mappings | ~620KB | Fast text search |
| `category_index.json` | Category → pattern mappings | ~1KB | Category filtering |
| `tag_index.json` | Tag → pattern mappings | ~20KB | Tag-based search |
| `company_index.json` | Company → pattern mappings | ~10KB | Company filtering |
| `search_suggestions.json` | Auto-complete suggestions | ~10KB | Search UX |
| `search_metadata.json` | Index statistics | ~1KB | Analytics |
| `search_analytics.json` | Detailed analytics | ~10KB | Insights |
| `example_search_queries.json` | Query examples | ~3KB | Documentation |

## 🔍 Search Capabilities

### 1. Text Search
- **Full-text search** across titles, descriptions, content
- **Synonym matching** (e.g., "async" matches "asynchronous")
- **Partial word matching** with relevance scoring
- **Multi-word queries** with phrase detection

### 2. Filtering
- **Category**: Architecture, Resilience, Data Management, etc.
- **Excellence Tier**: Gold, Silver, Bronze
- **Difficulty**: Beginner, Intermediate, Advanced
- **Company**: Netflix, Google, Amazon, Uber, etc.
- **Status**: Recommended, Stable, Legacy, etc.
- **Tags**: Microservices, Real-time, Security, etc.

### 3. Smart Features
- **Auto-complete suggestions** based on popular searches
- **Related patterns** using tag and category similarity
- **Relevance scoring** considering tier, popularity, recency
- **Search analytics** for optimization insights

## 💻 Frontend Integration Examples

### Basic JavaScript Usage

```javascript
// Load the search interface
const searchInterface = new PatternSearchInterface('./search_index/');

// Wait for initialization
await searchInterface.loadSearchIndex();

// Perform searches
const results = searchInterface.search('circuit breaker');
const filtered = searchInterface.search('microservices', {
    tier: 'gold',
    category: 'architecture'
});

// Get suggestions
const suggestions = searchInterface.getSuggestions('circ', 5);

// Get related patterns
const related = searchInterface.getRelatedPatterns(pattern, 5);
```

### React Hook Example

```jsx
import { useState, useEffect } from 'react';

function usePatternSearch(indexPath = './search_index/') {
    const [searchInterface, setSearchInterface] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        const interface = new PatternSearchInterface(indexPath);
        interface.loadSearchIndex().then(() => {
            setSearchInterface(interface);
            setLoading(false);
        });
    }, [indexPath]);
    
    const search = (query, filters = {}) => {
        return searchInterface?.search(query, filters) || [];
    };
    
    return { search, loading, searchInterface };
}

// Usage in component
function PatternSearch() {
    const { search, loading } = usePatternSearch();
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    
    useEffect(() => {
        if (!loading && query) {
            const searchResults = search(query);
            setResults(searchResults);
        }
    }, [query, loading, search]);
    
    return (
        <div>
            <input 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search patterns..."
            />
            {results.map(pattern => (
                <PatternCard key={pattern.id} pattern={pattern} />
            ))}
        </div>
    );
}
```

### Vue.js Composition API

```vue
<script setup>
import { ref, computed, onMounted } from 'vue';

const searchInterface = ref(null);
const query = ref('');
const filters = ref({
    category: 'all',
    tier: 'all'
});

const results = computed(() => {
    if (!searchInterface.value || !query.value) return [];
    return searchInterface.value.search(query.value, filters.value);
});

onMounted(async () => {
    const interface = new PatternSearchInterface('./search_index/');
    await interface.loadSearchIndex();
    searchInterface.value = interface;
});
</script>

<template>
    <div class="pattern-search">
        <input v-model="query" placeholder="Search patterns...">
        <select v-model="filters.tier">
            <option value="all">All Tiers</option>
            <option value="gold">Gold</option>
            <option value="silver">Silver</option>
        </select>
        <div v-for="pattern in results" :key="pattern.id">
            <h3>{{ pattern.title }}</h3>
            <p>{{ pattern.description }}</p>
        </div>
    </div>
</template>
```

## 🚀 Advanced Search Examples

### 1. Fuzzy Search Implementation

```javascript
class FuzzyPatternSearch extends PatternSearchInterface {
    fuzzySearch(query, threshold = 0.6) {
        const results = [];
        
        for (const pattern of this.patterns) {
            const titleSimilarity = this.calculateSimilarity(query, pattern.title);
            const descSimilarity = this.calculateSimilarity(query, pattern.description);
            
            const maxSimilarity = Math.max(titleSimilarity, descSimilarity);
            
            if (maxSimilarity >= threshold) {
                results.push({
                    ...pattern,
                    similarity: maxSimilarity,
                    searchScore: maxSimilarity * 100
                });
            }
        }
        
        return results.sort((a, b) => b.similarity - a.similarity);
    }
    
    calculateSimilarity(str1, str2) {
        // Levenshtein distance implementation
        // ... implementation details
    }
}
```

### 2. Semantic Search with Embeddings

```javascript
class SemanticPatternSearch extends PatternSearchInterface {
    constructor(indexPath, embeddingsPath) {
        super(indexPath);
        this.embeddings = null;
        this.loadEmbeddings(embeddingsPath);
    }
    
    async semanticSearch(query, topK = 10) {
        if (!this.embeddings) return [];
        
        const queryEmbedding = await this.getQueryEmbedding(query);
        const similarities = [];
        
        for (const pattern of this.patterns) {
            const patternEmbedding = this.embeddings[pattern.id];
            if (patternEmbedding) {
                const similarity = this.cosineSimilarity(queryEmbedding, patternEmbedding);
                similarities.push({ pattern, similarity });
            }
        }
        
        return similarities
            .sort((a, b) => b.similarity - a.similarity)
            .slice(0, topK)
            .map(item => ({
                ...item.pattern,
                searchScore: item.similarity * 100
            }));
    }
}
```

### 3. Multi-Modal Search (Text + Categories + Tags)

```javascript
class MultiModalSearch extends PatternSearchInterface {
    searchMultiModal(options) {
        const {
            textQuery = '',
            categories = [],
            tags = [],
            companies = [],
            minTier = null,
            maxResults = 50
        } = options;
        
        let candidates = this.patterns;
        
        // Filter by categories
        if (categories.length > 0) {
            candidates = candidates.filter(p => categories.includes(p.category));
        }
        
        // Filter by tags
        if (tags.length > 0) {
            candidates = candidates.filter(p => 
                tags.some(tag => p.tags.includes(tag))
            );
        }
        
        // Filter by companies
        if (companies.length > 0) {
            candidates = candidates.filter(p =>
                companies.some(company => p.companies.includes(company))
            );
        }
        
        // Filter by tier
        if (minTier) {
            const tierOrder = { bronze: 0, silver: 1, gold: 2 };
            const minTierValue = tierOrder[minTier];
            candidates = candidates.filter(p => 
                tierOrder[p.excellence_tier] >= minTierValue
            );
        }
        
        // Apply text search if provided
        if (textQuery) {
            const textResults = this.performTextSearch(textQuery, {});
            const textResultIds = new Set(textResults.map(r => r.id));
            candidates = candidates.filter(p => textResultIds.has(p.id));
        }
        
        return candidates.slice(0, maxResults);
    }
}
```

## 📊 Search Analytics & Monitoring

### Track Search Performance

```javascript
class SearchAnalytics {
    constructor() {
        this.searchHistory = [];
        this.popularQueries = new Map();
        this.noResultQueries = [];
    }
    
    trackSearch(query, resultCount, filters = {}) {
        const searchEvent = {
            query,
            resultCount,
            filters,
            timestamp: new Date().toISOString(),
            sessionId: this.getSessionId()
        };
        
        this.searchHistory.push(searchEvent);
        
        // Update popular queries
        const count = this.popularQueries.get(query) || 0;
        this.popularQueries.set(query, count + 1);
        
        // Track no-result queries
        if (resultCount === 0) {
            this.noResultQueries.push(searchEvent);
        }
    }
    
    getSearchInsights() {
        return {
            totalSearches: this.searchHistory.length,
            uniqueQueries: new Set(this.searchHistory.map(s => s.query)).size,
            avgResultCount: this.searchHistory.reduce((sum, s) => sum + s.resultCount, 0) / this.searchHistory.length,
            noResultRate: this.noResultQueries.length / this.searchHistory.length,
            popularQueries: Array.from(this.popularQueries.entries())
                .sort((a, b) => b[1] - a[1])
                .slice(0, 10),
            recentSearches: this.searchHistory.slice(-20)
        };
    }
}
```

## 🎯 Search Query Examples by Use Case

### Finding Patterns for Specific Problems

```javascript
// High availability patterns
const haPatterns = searchInterface.search('high availability fault tolerance');

// Microservices decomposition
const microservicesPatterns = searchInterface.search('microservices', {
    category: 'architecture',
    tier: 'gold'
});

// Real-time data processing
const realTimePatterns = searchInterface.search('real-time streaming event', {
    tag: 'realtime'
});

// Netflix-proven patterns
const netflixPatterns = searchInterface.search('netflix', {
    tier: 'gold'
});
```

### Company-Specific Pattern Discovery

```javascript
// Patterns used by tech giants
const techGiantPatterns = [
    ...searchInterface.search('netflix'),
    ...searchInterface.search('google'),
    ...searchInterface.search('amazon'),
    ...searchInterface.search('uber')
].filter((pattern, index, self) => 
    self.findIndex(p => p.id === pattern.id) === index
);

// Fintech patterns
const fintechPatterns = searchInterface.search('payment banking financial', {
    tag: 'fintech'
});
```

### Learning Path Generation

```javascript
// Beginner-friendly patterns
const beginnerPatterns = searchInterface.search('', {
    difficulty: 'beginner',
    tier: 'gold'
}).slice(0, 10);

// Advanced patterns for experts  
const expertPatterns = searchInterface.search('', {
    difficulty: 'advanced',
    tier: 'gold'
}).slice(0, 10);

// Category progression
const resilienceJourney = [
    ...searchInterface.search('health check', { category: 'resilience' }),
    ...searchInterface.search('timeout retry', { category: 'resilience' }),
    ...searchInterface.search('circuit breaker', { category: 'resilience' }),
    ...searchInterface.search('bulkhead', { category: 'resilience' })
];
```

## 🔧 Performance Optimization Tips

### 1. Index Loading Strategy

```javascript
// Lazy load less critical indexes
class OptimizedSearchInterface extends PatternSearchInterface {
    async loadSearchIndex() {
        // Load core indexes first
        const coreData = await Promise.all([
            fetch(`${this.indexPath}patterns.json`).then(r => r.json()),
            fetch(`${this.indexPath}inverted_index.json`).then(r => r.json())
        ]);
        
        this.patterns = coreData[0];
        this.invertedIndex = coreData[1];
        this.initialized = true;
        
        // Load secondary indexes in background
        this.loadSecondaryIndexes();
    }
    
    async loadSecondaryIndexes() {
        const [categoryIndex, suggestions] = await Promise.all([
            fetch(`${this.indexPath}category_index.json`).then(r => r.json()),
            fetch(`${this.indexPath}search_suggestions.json`).then(r => r.json())
        ]);
        
        this.categoryIndex = categoryIndex;
        this.searchSuggestions = suggestions;
    }
}
```

### 2. Search Result Caching

```javascript
class CachedSearchInterface extends PatternSearchInterface {
    constructor(indexPath) {
        super(indexPath);
        this.searchCache = new Map();
        this.maxCacheSize = 1000;
    }
    
    search(query, filters = {}) {
        const cacheKey = JSON.stringify({ query, filters });
        
        if (this.searchCache.has(cacheKey)) {
            return this.searchCache.get(cacheKey);
        }
        
        const results = super.search(query, filters);
        
        // Manage cache size
        if (this.searchCache.size >= this.maxCacheSize) {
            const firstKey = this.searchCache.keys().next().value;
            this.searchCache.delete(firstKey);
        }
        
        this.searchCache.set(cacheKey, results);
        return results;
    }
}
```

### 3. Incremental Search Updates

```javascript
class IncrementalSearchInterface extends PatternSearchInterface {
    async updatePattern(patternData) {
        // Update pattern in main array
        const existingIndex = this.patterns.findIndex(p => p.id === patternData.id);
        if (existingIndex >= 0) {
            this.patterns[existingIndex] = patternData;
        } else {
            this.patterns.push(patternData);
        }
        
        // Update inverted index
        this.updateInvertedIndex(patternData);
        
        // Update category indexes
        this.updateCategoryIndexes(patternData);
    }
    
    updateInvertedIndex(pattern) {
        // Remove old entries
        for (const [term, patternIds] of Object.entries(this.invertedIndex)) {
            patternIds.delete(pattern.id);
            if (patternIds.size === 0) {
                delete this.invertedIndex[term];
            }
        }
        
        // Add new entries
        const tokens = this.tokenizeText(`${pattern.title} ${pattern.description}`);
        for (const token of tokens) {
            if (!this.invertedIndex[token]) {
                this.invertedIndex[token] = new Set();
            }
            this.invertedIndex[token].add(pattern.id);
        }
    }
}
```

## 🔄 Rebuilding the Search Index

### Automated Rebuild Script

```bash
#!/bin/bash
# rebuild_search_index.sh

echo "🔍 Rebuilding pattern search index..."

# Run the index builder
python3 build_pattern_search_index.py \
    --pattern-dir /home/deepak/DStudio/docs/pattern-library \
    --output-dir /home/deepak/DStudio/scripts/search_index \
    --analytics

# Copy to web assets directory (if applicable)
if [ -d "/var/www/pattern-library/assets" ]; then
    echo "📋 Copying index to web assets..."
    cp -r /home/deepak/DStudio/scripts/search_index/* /var/www/pattern-library/assets/search_index/
fi

echo "✅ Search index rebuild complete!"
```

### Git Hook Integration

```bash
#!/bin/sh
# .git/hooks/post-receive

# Rebuild search index when patterns change
if git diff-tree -r --name-only HEAD~1 HEAD | grep -q "docs/pattern-library.*\.md"; then
    echo "Pattern files changed, rebuilding search index..."
    cd /home/deepak/DStudio/scripts
    python3 build_pattern_search_index.py --analytics
    echo "Search index updated!"
fi
```

## 📈 Integration with MkDocs/Documentation Sites

### MkDocs Plugin Integration

```python
# mkdocs_search_plugin.py
from mkdocs.plugins import BasePlugin
import json
import os

class PatternSearchPlugin(BasePlugin):
    def on_post_build(self, config):
        # Run search index builder after docs are built
        index_script = os.path.join(config['config_file_path'], 'scripts/build_pattern_search_index.py')
        pattern_dir = os.path.join(config['docs_dir'], 'pattern-library')
        output_dir = os.path.join(config['site_dir'], 'assets/search_index')
        
        os.system(f"python3 {index_script} --pattern-dir {pattern_dir} --output-dir {output_dir}")
        
        # Add search interface to the site
        search_js = os.path.join(config['config_file_path'], 'scripts/search_interface_example.js')
        site_js_dir = os.path.join(config['site_dir'], 'assets/js')
        os.makedirs(site_js_dir, exist_ok=True)
        
        import shutil
        shutil.copy(search_js, os.path.join(site_js_dir, 'pattern_search.js'))
```

## 🎓 Next Steps & Advanced Features

1. **Machine Learning Enhancements**
   - Pattern recommendation system
   - Search result personalization  
   - Query intention detection

2. **Real-time Features**
   - Live search suggestions
   - Pattern popularity tracking
   - Usage analytics dashboard

3. **API Development**
   - REST API for search functionality
   - GraphQL endpoint for complex queries
   - WebSocket for real-time updates

4. **Mobile Optimization**
   - Responsive search interface
   - Touch-friendly suggestions
   - Offline search capability

This search index provides a robust foundation for building sophisticated pattern discovery experiences that help developers find the right solutions for their distributed systems challenges.