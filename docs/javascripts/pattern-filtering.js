// Pattern Filtering System JavaScript

// Pattern data structure - updated with actual pattern-library URLs
const patterns = [
    // Communication Patterns
    { name: "API Gateway", category: "communication", tier: "gold", status: "recommended", description: "Single entry point for client requests", url: "/DStudio/pattern-library/communication/api-gateway/", tags: ["api", "routing", "aggregation"] },
    { name: "Publish-Subscribe", category: "communication", tier: "gold", status: "recommended", description: "Event-driven communication pattern for multiple consumers", url: "/DStudio/pattern-library/communication/publish-subscribe/", tags: ["events", "broadcast", "decoupling"] },
    { name: "Request-Reply", category: "communication", tier: "gold", status: "recommended", description: "Synchronous request-response communication pattern", url: "/DStudio/pattern-library/communication/request-reply/", tags: ["rpc", "sync", "api"] },
    { name: "Service Mesh", category: "communication", tier: "gold", status: "recommended", description: "Infrastructure layer for service communication", url: "/DStudio/pattern-library/communication/service-mesh/", tags: ["networking", "observability", "security"] },
    { name: "WebSocket", category: "communication", tier: "silver", status: "stable", description: "Full-duplex communication over TCP", url: "/DStudio/pattern-library/communication/websocket/", tags: ["real-time", "bidirectional", "streaming"] },
    { name: "Service Discovery", category: "communication", tier: "gold", status: "recommended", description: "Dynamically locate services in distributed systems", url: "/DStudio/pattern-library/communication/service-discovery/", tags: ["discovery", "registry", "dynamic"] },
    { name: "Service Registry", category: "communication", tier: "silver", status: "stable", description: "Central registry for service instances", url: "/DStudio/pattern-library/communication/service-registry/", tags: ["registry", "discovery", "management"] },
    { name: "gRPC", category: "communication", tier: "gold", status: "recommended", description: "High-performance RPC framework", url: "/DStudio/pattern-library/communication/grpc/", tags: ["rpc", "performance", "protobuf"] },
    
    // Resilience Patterns
    { name: "Circuit Breaker", category: "resilience", tier: "gold", status: "recommended", description: "Prevent cascading failures in distributed systems", url: "/DStudio/pattern-library/resilience/circuit-breaker/", tags: ["fault-tolerance", "stability"] },
    { name: "Retry with Backoff", category: "resilience", tier: "gold", status: "recommended", description: "Intelligent retry mechanism with exponential backoff", url: "/DStudio/pattern-library/resilience/retry-backoff/", tags: ["reliability", "error-handling"] },
    { name: "Bulkhead", category: "resilience", tier: "gold", status: "recommended", description: "Isolate resources to prevent total system failure", url: "/DStudio/pattern-library/resilience/bulkhead/", tags: ["isolation", "fault-tolerance"] },
    { name: "Timeout", category: "resilience", tier: "gold", status: "recommended", description: "Prevent indefinite waiting for responses", url: "/DStudio/pattern-library/resilience/timeout/", tags: ["reliability", "performance"] },
    { name: "Health Check", category: "resilience", tier: "gold", status: "recommended", description: "Monitor service health and availability", url: "/DStudio/pattern-library/resilience/health-check/", tags: ["monitoring", "availability"] },
    { name: "Failover", category: "resilience", tier: "gold", status: "recommended", description: "Automatic switching to backup systems", url: "/DStudio/pattern-library/resilience/failover/", tags: ["availability", "backup", "recovery"] },
    { name: "Graceful Degradation", category: "resilience", tier: "silver", status: "stable", description: "Reduce functionality to maintain availability", url: "/DStudio/pattern-library/resilience/graceful-degradation/", tags: ["availability", "fallback", "performance"] },
    { name: "Heartbeat", category: "resilience", tier: "silver", status: "stable", description: "Periodic health signals between components", url: "/DStudio/pattern-library/resilience/heartbeat/", tags: ["monitoring", "liveness", "detection"] },
    { name: "Load Shedding", category: "resilience", tier: "gold", status: "recommended", description: "Drop requests to prevent overload", url: "/DStudio/pattern-library/resilience/load-shedding/", tags: ["protection", "overload", "stability"] },
    { name: "Split Brain", category: "resilience", tier: "silver", status: "stable", description: "Handle network partitions in clusters", url: "/DStudio/pattern-library/resilience/split-brain/", tags: ["partition", "consensus", "cluster"] },
    { name: "Fault Tolerance", category: "resilience", tier: "silver", status: "stable", description: "Design systems to handle component failures", url: "/DStudio/pattern-library/resilience/fault-tolerance/", tags: ["reliability", "redundancy"] },
    
    // Data Management Patterns
    { name: "CQRS", category: "data-management", tier: "gold", status: "recommended", description: "Separate read and write models for scalability", url: "/DStudio/pattern-library/data-management/cqrs/", tags: ["scalability", "performance", "separation"] },
    { name: "Event Sourcing", category: "data-management", tier: "gold", status: "recommended", description: "Store state changes as immutable events", url: "/DStudio/pattern-library/data-management/event-sourcing/", tags: ["audit", "replay", "events"] },
    { name: "Saga", category: "data-management", tier: "gold", status: "recommended", description: "Manage distributed transactions across services", url: "/DStudio/pattern-library/data-management/saga/", tags: ["transactions", "consistency", "coordination"] },
    { name: "Change Data Capture", category: "data-management", tier: "gold", status: "recommended", description: "Track and capture database changes", url: "/DStudio/pattern-library/data-management/cdc/", tags: ["streaming", "replication", "events"] },
    { name: "Outbox Pattern", category: "data-management", tier: "gold", status: "recommended", description: "Reliable event publishing with transactions", url: "/DStudio/pattern-library/data-management/outbox/", tags: ["reliability", "events", "transactions"] },
    { name: "Consistent Hashing", category: "data-management", tier: "gold", status: "recommended", description: "Distribute data across nodes efficiently", url: "/DStudio/pattern-library/data-management/consistent-hashing/", tags: ["partitioning", "scalability", "distribution"] },
    { name: "Eventual Consistency", category: "data-management", tier: "silver", status: "stable", description: "Allow temporary inconsistencies for availability", url: "/DStudio/pattern-library/data-management/eventual-consistency/", tags: ["consistency", "cap", "availability"] },
    { name: "Materialized View", category: "data-management", tier: "silver", status: "stable", description: "Pre-computed query results for performance", url: "/DStudio/pattern-library/data-management/materialized-view/", tags: ["performance", "denormalization", "caching"] },
    { name: "Write-Ahead Log", category: "data-management", tier: "gold", status: "recommended", description: "Ensure durability with sequential writes", url: "/DStudio/pattern-library/data-management/write-ahead-log/", tags: ["durability", "recovery", "transactions"] },
    { name: "Distributed Lock", category: "coordination", tier: "gold", status: "recommended", description: "Mutual exclusion across distributed systems", url: "/DStudio/pattern-library/coordination/distributed-lock/", tags: ["synchronization", "mutex", "coordination"] },
    { name: "Leader Election", category: "coordination", tier: "gold", status: "recommended", description: "Elect a single leader among distributed nodes", url: "/DStudio/pattern-library/coordination/leader-election/", tags: ["consensus", "coordination", "leadership"] },
    
    // Coordination Patterns
    { name: "Consensus", category: "coordination", tier: "gold", status: "recommended", description: "Agreement among distributed nodes", url: "/DStudio/pattern-library/coordination/consensus/", tags: ["raft", "paxos", "agreement"] },
    { name: "Hybrid Logical Clocks", category: "coordination", tier: "silver", status: "stable", description: "Combine physical and logical time", url: "/DStudio/pattern-library/coordination/hlc/", tags: ["time", "causality", "hybrid"] },
    { name: "Logical Clocks", category: "coordination", tier: "silver", status: "stable", description: "Order events without synchronized clocks", url: "/DStudio/pattern-library/coordination/logical-clocks/", tags: ["ordering", "lamport", "time"] },
    { name: "Generation Clock", category: "coordination", tier: "silver", status: "stable", description: "Track configuration versions", url: "/DStudio/pattern-library/coordination/generation-clock/", tags: ["versioning", "configuration", "epochs"] },
    { name: "Lease", category: "coordination", tier: "silver", status: "stable", description: "Time-bound resource allocation", url: "/DStudio/pattern-library/coordination/lease/", tags: ["timeout", "resources", "coordination"] },
    { name: "Clock Sync", category: "coordination", tier: "silver", status: "stable", description: "Synchronize clocks across distributed nodes", url: "/DStudio/pattern-library/coordination/clock-sync/", tags: ["ntp", "time", "synchronization"] },
    
    // Architecture Patterns
    { name: "Sidecar", category: "architecture", tier: "gold", status: "recommended", description: "Deploy functionality alongside application", url: "/DStudio/pattern-library/architecture/sidecar/", tags: ["deployment", "separation", "proxy"] },
    { name: "Ambassador", category: "architecture", tier: "silver", status: "stable", description: "Proxy for external services", url: "/DStudio/pattern-library/architecture/ambassador/", tags: ["proxy", "external", "abstraction"] },
    { name: "Strangler Fig", category: "architecture", tier: "gold", status: "recommended", description: "Gradually replace legacy systems", url: "/DStudio/pattern-library/architecture/strangler-fig/", tags: ["migration", "legacy", "incremental"] },
    { name: "Backends for Frontends", category: "architecture", tier: "silver", status: "stable", description: "Separate backends for different frontends", url: "/DStudio/pattern-library/architecture/backends-for-frontends/", tags: ["api", "frontend", "optimization"] },
    { name: "Anti-Corruption Layer", category: "architecture", tier: "silver", status: "stable", description: "Isolate legacy systems from new code", url: "/DStudio/pattern-library/architecture/anti-corruption-layer/", tags: ["legacy", "isolation", "translation"] },
    { name: "Cell-Based Architecture", category: "architecture", tier: "gold", status: "recommended", description: "Isolated deployment units for resilience", url: "/DStudio/pattern-library/architecture/cell-based/", tags: ["isolation", "resilience", "blast-radius"] },
    { name: "Choreography", category: "architecture", tier: "silver", status: "stable", description: "Decentralized workflow coordination", url: "/DStudio/pattern-library/architecture/choreography/", tags: ["workflow", "decentralized", "events"] },
    { name: "Event-Driven Architecture", category: "architecture", tier: "gold", status: "recommended", description: "System driven by event production and consumption", url: "/DStudio/pattern-library/architecture/event-driven/", tags: ["events", "async", "decoupling"] },
    { name: "Serverless/FaaS", category: "architecture", tier: "silver", status: "stable", description: "Function-as-a-Service architecture", url: "/DStudio/pattern-library/architecture/serverless-faas/", tags: ["serverless", "functions", "auto-scaling"] },
    { name: "Shared Nothing", category: "architecture", tier: "gold", status: "recommended", description: "No shared state between nodes", url: "/DStudio/pattern-library/architecture/shared-nothing/", tags: ["isolation", "scalability", "stateless"] },
    
    // Scaling Patterns
    { name: "Load Balancing", category: "scaling", tier: "gold", status: "recommended", description: "Distribute load across multiple servers", url: "/DStudio/pattern-library/scaling/load-balancing/", tags: ["scalability", "distribution", "availability"] },
    { name: "Sharding", category: "scaling", tier: "gold", status: "recommended", description: "Partition data across multiple databases", url: "/DStudio/pattern-library/scaling/sharding/", tags: ["partitioning", "scalability", "database"] },
    { name: "Caching Strategies", category: "scaling", tier: "gold", status: "recommended", description: "Various caching patterns for performance", url: "/DStudio/pattern-library/scaling/caching-strategies/", tags: ["caching", "performance", "optimization"] },
    { name: "Priority Queue", category: "scaling", tier: "silver", status: "stable", description: "Process high-priority items first", url: "/DStudio/pattern-library/scaling/priority-queue/", tags: ["queue", "prioritization", "scheduling"] },
    { name: "Rate Limiting", category: "scaling", tier: "gold", status: "recommended", description: "Control request rate to prevent overload", url: "/DStudio/pattern-library/scaling/rate-limiting/", tags: ["throttling", "protection", "control"] },
    { name: "Backpressure", category: "scaling", tier: "gold", status: "recommended", description: "Flow control in streaming systems", url: "/DStudio/pattern-library/scaling/backpressure/", tags: ["flow-control", "streaming", "protection"] },
    { name: "Auto-scaling", category: "scaling", tier: "gold", status: "recommended", description: "Automatically adjust resources based on load", url: "/DStudio/pattern-library/scaling/auto-scaling/", tags: ["elasticity", "cost", "performance"] },
    { name: "Request Batching", category: "scaling", tier: "silver", status: "stable", description: "Group multiple requests for efficiency", url: "/DStudio/pattern-library/scaling/request-batching/", tags: ["batching", "efficiency", "throughput"] },
    { name: "Scatter-Gather", category: "scaling", tier: "silver", status: "stable", description: "Distribute work and collect results", url: "/DStudio/pattern-library/scaling/scatter-gather/", tags: ["parallelism", "aggregation", "performance"] },
    { name: "Database per Service", category: "scaling", tier: "gold", status: "recommended", description: "Each service owns its database", url: "/DStudio/pattern-library/scaling/database-per-service/", tags: ["microservices", "isolation", "scalability"] },
    { name: "Database Sharding", category: "scaling", tier: "gold", status: "recommended", description: "Horizontal partitioning of data", url: "/DStudio/pattern-library/scaling/database-sharding/", tags: ["partitioning", "horizontal-scaling", "database"] },
    { name: "Edge Computing", category: "scaling", tier: "silver", status: "stable", description: "Process data closer to the source", url: "/DStudio/pattern-library/scaling/edge-computing/", tags: ["edge", "latency", "distribution"] },
    { name: "Geographic Load Balancing", category: "scaling", tier: "gold", status: "recommended", description: "Route traffic based on geography", url: "/DStudio/pattern-library/scaling/geographic-load-balancing/", tags: ["geo", "routing", "latency"] },
    { name: "Horizontal Pod Autoscaler", category: "scaling", tier: "silver", status: "stable", description: "Kubernetes-based auto-scaling", url: "/DStudio/pattern-library/scaling/horizontal-pod-autoscaler/", tags: ["kubernetes", "auto-scaling", "containers"] },
    { name: "Content Delivery Network", category: "scaling", tier: "gold", status: "recommended", description: "Cache content at edge locations", url: "/DStudio/pattern-library/scaling/content-delivery-network/", tags: ["cdn", "edge", "caching"] },
    { name: "Multi-Region", category: "scaling", tier: "gold", status: "recommended", description: "Deploy across multiple geographic regions", url: "/DStudio/pattern-library/scaling/multi-region/", tags: ["geo", "availability", "disaster-recovery"] },
    
    // From patterns directory (specialized/uncategorized)
    { name: "ID Generation at Scale", category: "scaling", tier: "gold", status: "recommended", description: "Generate unique IDs in distributed systems", url: "/DStudio/pattern-library/scaling/id-generation-scale/", tags: ["uuid", "snowflake", "uniqueness"] },
    { name: "URL Normalization", category: "scaling", tier: "silver", status: "stable", description: "Standardize URLs for consistency", url: "/DStudio/pattern-library/scaling/url-normalization/", tags: ["web", "standardization", "crawling"] },
    { name: "Deduplication", category: "data-management", tier: "silver", status: "stable", description: "Remove duplicate data efficiently", url: "/DStudio/pattern-library/data-management/deduplication/", tags: ["storage", "efficiency", "cleanup"] },
    { name: "Analytics at Scale", category: "scaling", tier: "gold", status: "recommended", description: "Process large-scale analytics workloads", url: "/DStudio/pattern-library/scaling/analytics-scale/", tags: ["big-data", "analytics", "processing"] },
    { name: "Event Streaming", category: "architecture", tier: "silver", status: "stable", description: "Process continuous streams of events", url: "/DStudio/pattern-library/architecture/event-streaming/", tags: ["streaming", "real-time", "events"] },
    { name: "Valet Key", category: "architecture", tier: "silver", status: "stable", description: "Provide temporary direct access to resources", url: "/DStudio/pattern-library/architecture/valet-key/", tags: ["security", "access", "temporary"] },
    { name: "Queues and Streaming", category: "scaling", tier: "silver", status: "stable", description: "Comparison of queuing vs streaming patterns", url: "/DStudio/pattern-library/scaling/queues-streaming/", tags: ["messaging", "comparison", "architecture"] },
    { name: "Tunable Consistency", category: "data-management", tier: "silver", status: "stable", description: "Adjust consistency levels dynamically", url: "/DStudio/pattern-library/data-management/tunable-consistency/", tags: ["consistency", "flexibility", "trade-offs"] },
    { name: "Tile Caching", category: "scaling", tier: "silver", status: "stable", description: "Cache map tiles for performance", url: "/DStudio/pattern-library/scaling/tile-caching/", tags: ["maps", "caching", "geo"] },
    { name: "CAP Theorem", category: "architecture", tier: "bronze", status: "legacy", description: "Consistency, Availability, Partition tolerance trade-offs", url: "/DStudio/pattern-library/architecture/cap-theorem/", tags: ["theory", "trade-offs", "distributed"] },
    { name: "Bloom Filter", category: "specialized", tier: "gold", status: "recommended", description: "Probabilistic data structure for set membership", url: "/DStudio/patterns/bloom-filter/", tags: ["performance", "space-efficiency"] },
    { name: "Merkle Trees", category: "specialized", tier: "gold", status: "recommended", description: "Verify data integrity efficiently", url: "/DStudio/patterns/merkle-trees/", tags: ["integrity", "verification", "sync"] },
    { name: "CRDT", category: "specialized", tier: "gold", status: "recommended", description: "Conflict-free replicated data types", url: "/DStudio/patterns/crdt/", tags: ["consistency", "replication", "conflict-resolution"] },
    { name: "Actor Model", category: "specialized", tier: "bronze", status: "legacy", description: "Concurrent computation with actors", url: "/DStudio/patterns/actor-model/", tags: ["concurrency", "messaging", "isolation"] },
    { name: "Lambda Architecture", category: "specialized", tier: "bronze", status: "legacy", description: "Batch and stream processing architecture", url: "/DStudio/patterns/lambda-architecture/", tags: ["big-data", "batch", "stream"] },
    { name: "Kappa Architecture", category: "specialized", tier: "silver", status: "stable", description: "Stream-only processing architecture", url: "/DStudio/patterns/kappa-architecture/", tags: ["streaming", "simplification", "real-time"] },
    { name: "Data Lake", category: "specialized", tier: "bronze", status: "legacy", description: "Centralized repository for raw data", url: "/DStudio/patterns/data-lake/", tags: ["storage", "analytics", "big-data"] },
    { name: "Polyglot Persistence", category: "specialized", tier: "silver", status: "stable", description: "Use different databases for different needs", url: "/DStudio/patterns/polyglot-persistence/", tags: ["database", "optimization", "flexibility"] },
    { name: "Distributed Storage", category: "specialized", tier: "gold", status: "recommended", description: "Store data across multiple nodes", url: "/DStudio/patterns/distributed-storage/", tags: ["storage", "scalability", "redundancy"] },
    { name: "LSM Tree", category: "specialized", tier: "gold", status: "recommended", description: "Log-structured merge tree for write optimization", url: "/DStudio/patterns/lsm-tree/", tags: ["storage", "write-optimization", "database"] },
    { name: "Distributed Queue", category: "specialized", tier: "silver", status: "stable", description: "Scalable queue across multiple nodes", url: "/DStudio/patterns/distributed-queue/", tags: ["queue", "scalability"] },
    { name: "GraphQL Federation", category: "specialized", tier: "silver", status: "stable", description: "Distributed GraphQL schema composition", url: "/DStudio/patterns/graphql-federation/", tags: ["api", "graphql", "federation"] },
    { name: "CAS", category: "specialized", tier: "silver", status: "stable", description: "Compare and swap for atomic operations", url: "/DStudio/patterns/cas/", tags: ["atomicity", "concurrency", "lock-free"] },
    { name: "Chunking", category: "specialized", tier: "silver", status: "stable", description: "Process large datasets in smaller chunks", url: "/DStudio/patterns/chunking/", tags: ["batch", "memory", "streaming"] },
    { name: "Delta Sync", category: "specialized", tier: "silver", status: "stable", description: "Synchronize only changed data", url: "/DStudio/patterns/delta-sync/", tags: ["sync", "efficiency", "bandwidth"] },
    { name: "Emergent Leader", category: "specialized", tier: "silver", status: "stable", description: "Leadership emerges without explicit election", url: "/DStudio/patterns/emergent-leader/", tags: ["self-organization", "leadership", "emergence"] },
    { name: "Geo-Distribution", category: "specialized", tier: "silver", status: "stable", description: "Distribute system across geographic regions", url: "/DStudio/patterns/geo-distribution/", tags: ["geo", "distribution", "global"] },
    { name: "Geo-Replication", category: "specialized", tier: "silver", status: "stable", description: "Replicate data across geographic regions", url: "/DStudio/patterns/geo-replication/", tags: ["replication", "geo", "availability"] },
    { name: "Leader-Follower", category: "specialized", tier: "silver", status: "stable", description: "Master-slave replication pattern", url: "/DStudio/patterns/leader-follower/", tags: ["replication", "master-slave", "consistency"] },
    { name: "Low-High Water Marks", category: "specialized", tier: "silver", status: "stable", description: "Track replication progress", url: "/DStudio/patterns/low-high-water-marks/", tags: ["replication", "progress", "tracking"] },
    { name: "Read Repair", category: "specialized", tier: "silver", status: "stable", description: "Fix inconsistencies during read operations", url: "/DStudio/patterns/read-repair/", tags: ["consistency", "repair", "eventual-consistency"] },
    { name: "Segmented Log", category: "specialized", tier: "silver", status: "stable", description: "Split logs into segments for efficiency", url: "/DStudio/patterns/segmented-log/", tags: ["logging", "storage", "performance"] },
    { name: "Shared Database", category: "specialized", tier: "bronze", status: "legacy", description: "Multiple services share a database", url: "/DStudio/patterns/shared-database/", tags: ["anti-pattern", "coupling"] },
    { name: "State Watch", category: "specialized", tier: "silver", status: "stable", description: "Monitor state changes in distributed systems", url: "/DStudio/patterns/state-watch/", tags: ["monitoring", "notifications", "state"] }];

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
        'data-management': 'Data Management',
        'coordination': 'Coordination',
        'architectural': 'Architecture',
        'scaling': 'Scaling',
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