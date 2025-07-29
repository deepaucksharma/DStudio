// Pattern Filtering System JavaScript

// Pattern data structure
const patterns = [
    // Communication Patterns
    { name: "Message Queue", category: "communication", tier: "gold", status: "recommended", description: "Asynchronous message passing between services", url: "/patterns/message-queue/", tags: ["async", "decoupling", "scalability"] },
    { name: "Publish-Subscribe", category: "communication", tier: "gold", status: "recommended", description: "Event-driven communication pattern for multiple consumers", url: "/patterns/publish-subscribe/", tags: ["events", "broadcast", "decoupling"] },
    { name: "Request-Reply", category: "communication", tier: "gold", status: "recommended", description: "Synchronous request-response communication pattern", url: "/patterns/request-reply/", tags: ["rpc", "sync", "api"] },
    { name: "GraphQL Federation", category: "communication", tier: "silver", status: "stable", description: "Distributed GraphQL schema composition", url: "/patterns/graphql-federation/", tags: ["api", "graphql", "federation"] },
    { name: "Idempotent Receiver", category: "communication", tier: "gold", status: "recommended", description: "Handle duplicate messages safely", url: "/patterns/idempotent-receiver/", tags: ["reliability", "deduplication"] },
    { name: "Distributed Queue", category: "communication", tier: "silver", status: "stable", description: "Scalable queue across multiple nodes", url: "/patterns/distributed-queue/", tags: ["queue", "scalability"] },
    
    // Resilience Patterns
    { name: "Circuit Breaker", category: "resilience", tier: "gold", status: "recommended", description: "Prevent cascading failures in distributed systems", url: "/patterns/circuit-breaker/", tags: ["fault-tolerance", "stability"] },
    { name: "Retry with Backoff", category: "resilience", tier: "gold", status: "recommended", description: "Intelligent retry mechanism with exponential backoff", url: "/patterns/retry/", tags: ["reliability", "error-handling"] },
    { name: "Bulkhead", category: "resilience", tier: "gold", status: "recommended", description: "Isolate resources to prevent total system failure", url: "/patterns/bulkhead/", tags: ["isolation", "fault-tolerance"] },
    { name: "Timeout", category: "resilience", tier: "gold", status: "recommended", description: "Prevent indefinite waiting for responses", url: "/patterns/timeout/", tags: ["reliability", "performance"] },
    { name: "Health Check", category: "resilience", tier: "gold", status: "recommended", description: "Monitor service health and availability", url: "/patterns/health-check/", tags: ["monitoring", "availability"] },
    { name: "Fault Tolerance", category: "resilience", tier: "silver", status: "stable", description: "Design systems to handle component failures", url: "/patterns/fault-tolerance/", tags: ["reliability", "redundancy"] },
    { name: "Multi-Region", category: "resilience", tier: "gold", status: "recommended", description: "Deploy across multiple geographic regions", url: "/patterns/multi-region/", tags: ["geo", "availability", "disaster-recovery"] },
    
    // Data Management Patterns
    { name: "CQRS", category: "distributed-data", tier: "gold", status: "recommended", description: "Separate read and write models for scalability", url: "/patterns/cqrs/", tags: ["scalability", "performance", "separation"] },
    { name: "Event Sourcing", category: "distributed-data", tier: "gold", status: "recommended", description: "Store state changes as immutable events", url: "/patterns/event-sourcing/", tags: ["audit", "replay", "events"] },
    { name: "Saga", category: "distributed-data", tier: "gold", status: "recommended", description: "Manage distributed transactions across services", url: "/patterns/saga/", tags: ["transactions", "consistency", "coordination"] },
    { name: "Cache-Aside", category: "distributed-data", tier: "gold", status: "recommended", description: "Load data on demand into cache", url: "/patterns/cache-aside/", tags: ["caching", "performance"] },
    { name: "Write-Through Cache", category: "distributed-data", tier: "silver", status: "stable", description: "Write to cache and database simultaneously", url: "/patterns/write-through-cache/", tags: ["caching", "consistency"] },
    { name: "Write-Behind Cache", category: "distributed-data", tier: "silver", status: "stable", description: "Asynchronous write from cache to database", url: "/patterns/write-behind-cache/", tags: ["caching", "performance"] },
    { name: "Shared Database", category: "distributed-data", tier: "bronze", status: "legacy", description: "Multiple services share a database", url: "/patterns/shared-database/", tags: ["anti-pattern", "coupling"] },
    { name: "Database per Service", category: "distributed-data", tier: "gold", status: "recommended", description: "Each service owns its database", url: "/patterns/database-per-service/", tags: ["microservices", "isolation"] },
    { name: "CRDT", category: "distributed-data", tier: "gold", status: "recommended", description: "Conflict-free replicated data types", url: "/patterns/crdt/", tags: ["consistency", "replication", "conflict-resolution"] },
    { name: "Bloom Filter", category: "distributed-data", tier: "gold", status: "recommended", description: "Probabilistic data structure for set membership", url: "/patterns/bloom-filter/", tags: ["performance", "space-efficiency"] },
    { name: "Merkle Trees", category: "distributed-data", tier: "gold", status: "recommended", description: "Verify data integrity efficiently", url: "/patterns/merkle-trees/", tags: ["integrity", "verification", "sync"] },
    { name: "Geo-Replication", category: "distributed-data", tier: "silver", status: "stable", description: "Replicate data across geographic regions", url: "/patterns/geo-replication/", tags: ["replication", "geo", "availability"] },
    { name: "Data Mesh", category: "distributed-data", tier: "silver", status: "stable", description: "Decentralized data architecture", url: "/patterns/data-mesh/", tags: ["architecture", "decentralization", "ownership"] },
    { name: "Data Lake", category: "distributed-data", tier: "bronze", status: "legacy", description: "Centralized repository for raw data", url: "/patterns/data-lake/", tags: ["storage", "analytics", "big-data"] },
    { name: "Delta Sync", category: "distributed-data", tier: "silver", status: "stable", description: "Synchronize only changed data", url: "/patterns/delta-sync/", tags: ["sync", "efficiency", "bandwidth"] },
    { name: "Read Repair", category: "distributed-data", tier: "silver", status: "stable", description: "Fix inconsistencies during read operations", url: "/patterns/read-repair/", tags: ["consistency", "repair", "eventual-consistency"] },
    { name: "Distributed Storage", category: "distributed-data", tier: "gold", status: "recommended", description: "Store data across multiple nodes", url: "/patterns/distributed-storage/", tags: ["storage", "scalability", "redundancy"] },
    { name: "Polyglot Persistence", category: "distributed-data", tier: "silver", status: "stable", description: "Use different databases for different needs", url: "/patterns/polyglot-persistence/", tags: ["database", "optimization", "flexibility"] },
    { name: "Singleton Database", category: "distributed-data", tier: "bronze", status: "legacy", description: "Single database for all services", url: "/patterns/singleton-database/", tags: ["anti-pattern", "bottleneck"] },
    
    // Coordination Patterns
    { name: "Leader Election", category: "coordination", tier: "gold", status: "recommended", description: "Elect a single leader among distributed nodes", url: "/patterns/leader-election/", tags: ["consensus", "coordination", "leadership"] },
    { name: "Distributed Lock", category: "coordination", tier: "gold", status: "recommended", description: "Mutual exclusion across distributed systems", url: "/patterns/distributed-lock/", tags: ["synchronization", "mutex", "coordination"] },
    { name: "Two-Phase Commit", category: "coordination", tier: "bronze", status: "legacy", description: "Atomic commit protocol for distributed transactions", url: "/patterns/two-phase-commit/", tags: ["transactions", "atomicity", "blocking"] },
    { name: "Three-Phase Commit", category: "coordination", tier: "bronze", status: "legacy", description: "Non-blocking atomic commit protocol", url: "/patterns/three-phase-commit/", tags: ["transactions", "atomicity", "non-blocking"] },
    { name: "Consensus", category: "coordination", tier: "gold", status: "recommended", description: "Agreement among distributed nodes", url: "/patterns/consensus/", tags: ["raft", "paxos", "agreement"] },
    { name: "Vector Clock", category: "coordination", tier: "silver", status: "stable", description: "Track causality in distributed systems", url: "/patterns/vector-clock/", tags: ["causality", "ordering", "time"] },
    { name: "Logical Clocks", category: "coordination", tier: "silver", status: "stable", description: "Order events without synchronized clocks", url: "/patterns/logical-clocks/", tags: ["ordering", "lamport", "time"] },
    { name: "HLC", category: "coordination", tier: "silver", status: "stable", description: "Hybrid logical clocks combining physical and logical time", url: "/patterns/hlc/", tags: ["time", "causality", "hybrid"] },
    { name: "Clock Sync", category: "coordination", tier: "silver", status: "stable", description: "Synchronize clocks across distributed nodes", url: "/patterns/clock-sync/", tags: ["ntp", "time", "synchronization"] },
    { name: "Lease", category: "coordination", tier: "silver", status: "stable", description: "Time-bound resource allocation", url: "/patterns/lease/", tags: ["timeout", "resources", "coordination"] },
    { name: "State Watch", category: "coordination", tier: "silver", status: "stable", description: "Monitor state changes in distributed systems", url: "/patterns/state-watch/", tags: ["monitoring", "notifications", "state"] },
    { name: "Generation Clock", category: "coordination", tier: "silver", status: "stable", description: "Track configuration versions", url: "/patterns/generation-clock/", tags: ["versioning", "configuration", "epochs"] },
    { name: "Leader-Follower", category: "coordination", tier: "silver", status: "stable", description: "Master-slave replication pattern", url: "/patterns/leader-follower/", tags: ["replication", "master-slave", "consistency"] },
    { name: "Emergent Leader", category: "coordination", tier: "silver", status: "stable", description: "Leadership emerges without explicit election", url: "/patterns/emergent-leader/", tags: ["self-organization", "leadership", "emergence"] },
    { name: "CAS", category: "coordination", tier: "silver", status: "stable", description: "Compare and swap for atomic operations", url: "/patterns/cas/", tags: ["atomicity", "concurrency", "lock-free"] },
    
    // Architecture Patterns
    { name: "Microservices", category: "architectural", tier: "gold", status: "recommended", description: "Decompose applications into small services", url: "/patterns/microservices/", tags: ["architecture", "decomposition", "scalability"] },
    { name: "Service Mesh", category: "architectural", tier: "gold", status: "recommended", description: "Infrastructure layer for service communication", url: "/patterns/service-mesh/", tags: ["networking", "observability", "security"] },
    { name: "API Gateway", category: "architectural", tier: "gold", status: "recommended", description: "Single entry point for client requests", url: "/patterns/api-gateway/", tags: ["api", "routing", "aggregation"] },
    { name: "Sidecar", category: "architectural", tier: "gold", status: "recommended", description: "Deploy functionality alongside application", url: "/patterns/sidecar/", tags: ["deployment", "separation", "proxy"] },
    { name: "Backend for Frontend", category: "architectural", tier: "silver", status: "stable", description: "Separate backends for different frontends", url: "/patterns/bff/", tags: ["api", "frontend", "optimization"] },
    { name: "Gateway Routing", category: "architectural", tier: "silver", status: "stable", description: "Route requests to appropriate services", url: "/patterns/gateway-routing/", tags: ["routing", "load-balancing", "api"] },
    { name: "Strangler Fig", category: "architectural", tier: "gold", status: "recommended", description: "Gradually replace legacy systems", url: "/patterns/strangler-fig/", tags: ["migration", "legacy", "incremental"] },
    { name: "Lambda Architecture", category: "architectural", tier: "bronze", status: "legacy", description: "Batch and stream processing architecture", url: "/patterns/lambda-architecture/", tags: ["big-data", "batch", "stream"] },
    { name: "Kappa Architecture", category: "architectural", tier: "silver", status: "stable", description: "Stream-only processing architecture", url: "/patterns/kappa-architecture/", tags: ["streaming", "simplification", "real-time"] },
    { name: "Thick Client", category: "architectural", tier: "bronze", status: "legacy", description: "Heavy client-side processing", url: "/patterns/thick-client/", tags: ["client", "processing", "desktop"] },
    { name: "Stored Procedures", category: "architectural", tier: "bronze", status: "legacy", description: "Business logic in database", url: "/patterns/stored-procedures/", tags: ["database", "logic", "coupling"] },
    { name: "Actor Model", category: "architectural", tier: "bronze", status: "legacy", description: "Concurrent computation with actors", url: "/patterns/actor-model/", tags: ["concurrency", "messaging", "isolation"] },
    
    // Performance Patterns
    { name: "Load Balancer", category: "performance", tier: "gold", status: "recommended", description: "Distribute load across multiple servers", url: "/patterns/load-balancer/", tags: ["scalability", "distribution", "availability"] },
    { name: "Auto-scaling", category: "performance", tier: "gold", status: "recommended", description: "Automatically adjust resources based on load", url: "/patterns/auto-scaling/", tags: ["elasticity", "cost", "performance"] },
    { name: "CDN", category: "performance", tier: "gold", status: "recommended", description: "Content delivery network for static assets", url: "/patterns/cdn/", tags: ["caching", "edge", "latency"] },
    { name: "Database Sharding", category: "performance", tier: "gold", status: "recommended", description: "Partition data across multiple databases", url: "/patterns/sharding/", tags: ["partitioning", "scalability", "database"] },
    { name: "Read Replicas", category: "performance", tier: "gold", status: "recommended", description: "Scale read operations with replicas", url: "/patterns/read-replicas/", tags: ["replication", "read-scaling", "performance"] },
    { name: "Connection Pooling", category: "performance", tier: "gold", status: "recommended", description: "Reuse database connections efficiently", url: "/patterns/connection-pooling/", tags: ["optimization", "resources", "database"] },
    { name: "Lazy Loading", category: "performance", tier: "silver", status: "stable", description: "Load data only when needed", url: "/patterns/lazy-loading/", tags: ["optimization", "on-demand", "efficiency"] },
    { name: "Eager Loading", category: "performance", tier: "silver", status: "stable", description: "Preload related data to avoid N+1 queries", url: "/patterns/eager-loading/", tags: ["optimization", "preloading", "database"] },
    { name: "Chunking", category: "performance", tier: "silver", status: "stable", description: "Process large datasets in smaller chunks", url: "/patterns/chunking/", tags: ["batch", "memory", "streaming"] },
    { name: "Adaptive Scheduling", category: "performance", tier: "silver", status: "stable", description: "Dynamically adjust task scheduling", url: "/patterns/adaptive-scheduling/", tags: ["scheduling", "optimization", "dynamic"] },
    { name: "LSM Tree", category: "performance", tier: "gold", status: "recommended", description: "Log-structured merge tree for write optimization", url: "/patterns/lsm-tree/", tags: ["storage", "write-optimization", "database"] },
    
    // Specialized Patterns
    { name: "Geohashing", category: "specialized", tier: "silver", status: "stable", description: "Encode geographic coordinates efficiently", url: "/patterns/geohashing/", tags: ["geo", "spatial", "indexing"] },
    { name: "Quadtree", category: "specialized", tier: "silver", status: "stable", description: "Spatial indexing for 2D space", url: "/patterns/quadtree/", tags: ["spatial", "indexing", "search"] },
    { name: "R-tree", category: "specialized", tier: "silver", status: "stable", description: "Spatial indexing for multi-dimensional data", url: "/patterns/r-tree/", tags: ["spatial", "indexing", "multi-dimensional"] },
    { name: "Time-series Database", category: "specialized", tier: "gold", status: "recommended", description: "Optimized storage for time-series data", url: "/patterns/time-series-db/", tags: ["metrics", "monitoring", "iot"] },
    { name: "Blockchain", category: "specialized", tier: "silver", status: "stable", description: "Distributed ledger with immutable records", url: "/patterns/blockchain/", tags: ["immutability", "distributed-ledger", "consensus"] },
    { name: "ID Generation at Scale", category: "specialized", tier: "gold", status: "recommended", description: "Generate unique IDs in distributed systems", url: "/patterns/id-generation-scale/", tags: ["uuid", "snowflake", "uniqueness"] },
    { name: "URL Normalization", category: "specialized", tier: "silver", status: "stable", description: "Standardize URLs for consistency", url: "/patterns/url-normalization/", tags: ["web", "standardization", "crawling"] },
    { name: "Deduplication", category: "specialized", tier: "silver", status: "stable", description: "Remove duplicate data efficiently", url: "/patterns/deduplication/", tags: ["storage", "efficiency", "cleanup"] },
    { name: "Analytics at Scale", category: "specialized", tier: "gold", status: "recommended", description: "Process large-scale analytics workloads", url: "/patterns/analytics-scale/", tags: ["big-data", "analytics", "processing"] },
    { name: "Event Streaming", category: "specialized", tier: "silver", status: "stable", description: "Process continuous streams of events", url: "/patterns/event-streaming/", tags: ["streaming", "real-time", "events"] },
    { name: "Request Routing", category: "specialized", tier: "silver", status: "stable", description: "Direct requests to appropriate handlers", url: "/patterns/request-routing/", tags: ["routing", "dispatch", "handling"] },
    { name: "Valet Key", category: "specialized", tier: "silver", status: "stable", description: "Provide temporary direct access to resources", url: "/patterns/valet-key/", tags: ["security", "access", "temporary"] },
    { name: "Queues and Streaming", category: "specialized", tier: "silver", status: "stable", description: "Comparison of queuing vs streaming patterns", url: "/patterns/queues-streaming/", tags: ["messaging", "comparison", "architecture"] },
    { name: "Tunable Consistency", category: "specialized", tier: "silver", status: "stable", description: "Adjust consistency levels dynamically", url: "/patterns/tunable-consistency/", tags: ["consistency", "flexibility", "trade-offs"] },
    { name: "Time Series IDs", category: "specialized", tier: "silver", status: "stable", description: "Generate IDs for time-series data", url: "/patterns/time-series-ids/", tags: ["time-series", "ids", "ordering"] },
    { name: "Tile Caching", category: "specialized", tier: "silver", status: "stable", description: "Cache map tiles for performance", url: "/patterns/tile-caching/", tags: ["maps", "caching", "geo"] },
    { name: "Spatial Indexing", category: "specialized", tier: "silver", status: "stable", description: "Index spatial data for efficient queries", url: "/patterns/spatial-indexing/", tags: ["spatial", "indexing", "geo"] },
    { name: "CAP Theorem", category: "specialized", tier: "bronze", status: "legacy", description: "Consistency, Availability, Partition tolerance trade-offs", url: "/patterns/cap-theorem/", tags: ["theory", "trade-offs", "distributed"] }
];

// State management
let currentFilters = {
    search: '',
    tier: 'all',
    category: 'all'
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Load saved filters from localStorage
    loadSavedFilters();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initial render
    renderPatterns();
});

// Load saved filters from localStorage
function loadSavedFilters() {
    const saved = localStorage.getItem('patternFilters');
    if (saved) {
        try {
            const parsed = JSON.parse(saved);
            currentFilters = { ...currentFilters, ...parsed };
            
            // Apply saved filters to UI
            document.getElementById('pattern-search').value = currentFilters.search || '';
            
            // Update active buttons
            updateActiveButtons();
        } catch (e) {
            console.error('Error loading saved filters:', e);
        }
    }
}

// Save filters to localStorage
function saveFilters() {
    localStorage.setItem('patternFilters', JSON.stringify(currentFilters));
}

// Set up event listeners
function setupEventListeners() {
    // Search input
    const searchInput = document.getElementById('pattern-search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            currentFilters.search = e.target.value.toLowerCase();
            saveFilters();
            renderPatterns();
        }, 300));
    }
    
    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const filterType = this.dataset.filter;
            const filterValue = this.dataset.value;
            
            // Update current filters
            currentFilters[filterType] = filterValue;
            
            // Update active state
            updateActiveButtons();
            
            // Save and render
            saveFilters();
            renderPatterns();
        });
    });
}

// Update active button states
function updateActiveButtons() {
    // Update tier buttons
    document.querySelectorAll('[data-filter="tier"]').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.value === currentFilters.tier);
    });
    
    // Update category buttons
    document.querySelectorAll('[data-filter="category"]').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.value === currentFilters.category);
    });
}

// Reset all filters
function resetFilters() {
    currentFilters = {
        search: '',
        tier: 'all',
        category: 'all'
    };
    
    // Clear search input
    document.getElementById('pattern-search').value = '';
    
    // Update buttons
    updateActiveButtons();
    
    // Save and render
    saveFilters();
    renderPatterns();
}

// Render patterns based on current filters
function renderPatterns() {
    const container = document.getElementById('pattern-grid');
    if (!container) return;
    
    // Filter patterns
    const filtered = patterns.filter(pattern => {
        // Search filter
        if (currentFilters.search) {
            const searchTerm = currentFilters.search;
            const matchesSearch = pattern.name.toLowerCase().includes(searchTerm) ||
                                pattern.description.toLowerCase().includes(searchTerm) ||
                                pattern.category.toLowerCase().includes(searchTerm) ||
                                pattern.tags.some(tag => tag.toLowerCase().includes(searchTerm));
            if (!matchesSearch) return false;
        }
        
        // Tier filter
        if (currentFilters.tier !== 'all' && pattern.tier !== currentFilters.tier) {
            return false;
        }
        
        // Category filter
        if (currentFilters.category !== 'all' && pattern.category !== currentFilters.category) {
            return false;
        }
        
        return true;
    });
    
    // Update count
    updatePatternCount(filtered.length, patterns.length);
    
    // Clear container
    container.innerHTML = '';
    
    // Render patterns or no results message
    if (filtered.length === 0) {
        container.innerHTML = `
            <div class="no-results">
                <h3>No patterns found</h3>
                <p>Try adjusting your filters or search term</p>
            </div>
        `;
    } else {
        filtered.forEach(pattern => {
            container.appendChild(createPatternCard(pattern));
        });
    }
}

// Create pattern card element
function createPatternCard(pattern) {
    const card = document.createElement('div');
    card.className = 'pattern-card';
    
    const tierEmoji = {
        gold: '🥇',
        silver: '🥈',
        bronze: '🥉'
    }[pattern.tier] || '';
    
    const statusClass = pattern.status.toLowerCase().replace(/\s+/g, '-');
    
    card.innerHTML = `
        <div class="pattern-header">
            <a href="${pattern.url}" class="pattern-title">${pattern.name}</a>
            <span class="pattern-tier">${tierEmoji}</span>
        </div>
        <div class="pattern-meta">
            <span class="pattern-category">${formatCategory(pattern.category)}</span>
            <span class="pattern-status ${statusClass}">${pattern.status}</span>
        </div>
        <p class="pattern-description">${pattern.description}</p>
        <div class="pattern-tags">
            ${pattern.tags.map(tag => `<span class="pattern-tag">${tag}</span>`).join('')}
        </div>
    `;
    
    return card;
}

// Format category name for display
function formatCategory(category) {
    const categoryMap = {
        'communication': 'Communication',
        'resilience': 'Resilience',
        'distributed-data': 'Data Management',
        'coordination': 'Coordination',
        'architectural': 'Architecture',
        'performance': 'Performance',
        'specialized': 'Specialized'
    };
    return categoryMap[category] || category;
}

// Update pattern count display
function updatePatternCount(filtered, total) {
    const filteredSpan = document.getElementById('filtered-count');
    const totalSpan = document.getElementById('total-count');
    
    if (filteredSpan) filteredSpan.textContent = filtered;
    if (totalSpan) totalSpan.textContent = total;
}

// Debounce function for search input
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}