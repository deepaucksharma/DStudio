---
title: Pattern Catalog - Complete Reference
description: Comprehensive sortable and filterable catalog of all distributed systems patterns
---

# Pattern Catalog

**Complete reference of all 101 distributed systems patterns with excellence tier classifications**

<div class="catalog-controls" style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;">
    <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
        <input type="text" id="catalog-search" placeholder="Search patterns..." 
               style="flex: 1; min-width: 200px; padding: 0.5rem; border: 1px solid #e5e7eb; border-radius: 4px;"
               onkeyup="filterCatalog()">
        
        <select id="tier-filter" onchange="filterCatalog()" 
                style="padding: 0.5rem; border: 1px solid #e5e7eb; border-radius: 4px;">
            <option value="">All Tiers</option>
            <option value="gold">🥇 Gold Only</option>
            <option value="silver">🥈 Silver Only</option>
            <option value="bronze">🥉 Bronze Only</option>
        </select>
        
        <select id="category-filter" onchange="filterCatalog()" 
                style="padding: 0.5rem; border: 1px solid #e5e7eb; border-radius: 4px;">
            <option value="">All Categories</option>
            <option value="core">🏗️ Core</option>
            <option value="resilience">🛡️ Resilience</option>
            <option value="data">💾 Data</option>
            <option value="coordination">🤝 Coordination</option>
            <option value="operational">⚙️ Operational</option>
        </select>
        
        <button onclick="exportCatalog()" 
                style="background: #5448C8; color: white; padding: 0.5rem 1.5rem; border: none; border-radius: 4px; cursor: pointer;">
            Export CSV
        </button>
    </div>
</div>

## Pattern Excellence Distribution

<div class="tier-summary" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
    <div style="background: linear-gradient(135deg, #FFD700 0%, #FFF8DC 100%); padding: 1.5rem; border-radius: 8px; text-align: center;">
        <h3 style="margin: 0;">🥇 Gold Tier</h3>
        <p style="font-size: 2rem; margin: 0.5rem 0;">38</p>
        <p style="margin: 0; font-size: 0.9rem;">Battle-tested at FAANG scale</p>
    </div>
    <div style="background: linear-gradient(135deg, #C0C0C0 0%, #F5F5F5 100%); padding: 1.5rem; border-radius: 8px; text-align: center;">
        <h3 style="margin: 0;">🥈 Silver Tier</h3>
        <p style="font-size: 2rem; margin: 0.5rem 0;">38</p>
        <p style="margin: 0; font-size: 0.9rem;">Proven in production</p>
    </div>
    <div style="background: linear-gradient(135deg, #CD7F32 0%, #F4A460 100%); padding: 1.5rem; border-radius: 8px; text-align: center; color: white;">
        <h3 style="margin: 0;">🥉 Bronze Tier</h3>
        <p style="font-size: 2rem; margin: 0.5rem 0;">25</p>
        <p style="margin: 0; font-size: 0.9rem;">Well-documented approach</p>
    </div>
</div>

## Complete Pattern Catalog

<div id="catalog-table-container">

| Pattern Name | Excellence Tier | Category | Status | Use When | Link |
|--------------|-----------------|----------|---------|-----------|------|
| **Circuit Breaker** | 🥇 Gold | 🛡️ Resilience | Production-ready | Preventing cascade failures in microservices | [→](circuit-breaker.md) |
| **Retry & Backoff** | 🥇 Gold | 🛡️ Resilience | Production-ready | Handling transient failures gracefully | [→](retry-backoff.md) |
| **Load Balancing** | 🥇 Gold | ⚙️ Operational | Production-ready | Distributing traffic across multiple instances | [→](load-balancing.md) |
| **Caching Strategies** | 🥇 Gold | 💾 Data | Production-ready | Reducing latency and database load | [→](caching-strategies.md) |
| **Health Check** | 🥇 Gold | ⚙️ Operational | Production-ready | Monitoring service availability and health | [→](health-check.md) |
| **CQRS** | 🥇 Gold | 🏗️ Core | Production-ready | Separating read and write operations at scale | [→](cqrs.md) |
| **Sharding** | 🥇 Gold | 💾 Data | Production-ready | Horizontal data partitioning for scale | [→](sharding.md) |
| **API Gateway** | 🥇 Gold | 🏗️ Core | Production-ready | Single entry point for microservices | [→](api-gateway.md) |
| **Leader-Follower** | 🥇 Gold | 💾 Data | Production-ready | Database replication with single writer | [→](leader-follower.md) |
| **Consistent Hashing** | 🥇 Gold | 💾 Data | Production-ready | Dynamic node addition/removal in clusters | [→](consistent-hashing.md) |
| **Rate Limiting** | 🥇 Gold | 🛡️ Resilience | Production-ready | Protecting APIs from overload | [→](rate-limiting.md) |
| **Timeout** | 🥇 Gold | 🛡️ Resilience | Production-ready | Preventing indefinite resource blocking | [→](timeout.md) |
| **Failover** | 🥇 Gold | 🛡️ Resilience | Production-ready | Automatic recovery from node failures | [→](failover.md) |
| **Auto-scaling** | 🥇 Gold | ⚙️ Operational | Production-ready | Dynamic capacity based on load | [→](auto-scaling.md) |
| **Consensus** | 🥇 Gold | 🤝 Coordination | Production-ready | Distributed agreement (Raft/Paxos) | [→](consensus.md) |
| **Distributed Queue** | 🥇 Gold | 🏗️ Core | Production-ready | Asynchronous task processing | [→](distributed-queue.md) |
| **Publish-Subscribe** | 🥇 Gold | 🏗️ Core | Production-ready | Event distribution to multiple consumers | [→](publish-subscribe.md) |
| **Observability** | 🥇 Gold | ⚙️ Operational | Production-ready | Comprehensive system monitoring | [→](observability.md) |
| **Blue-Green Deployment** | 🥇 Gold | ⚙️ Operational | Production-ready | Zero-downtime deployments | [→](blue-green-deployment.md) |
| **WAL** | 🥇 Gold | 💾 Data | Production-ready | Durability guarantees for databases | [→](wal.md) |
| **Database per Service** | 🥇 Gold | 💾 Data | Production-ready | Service autonomy in microservices | [→](database-per-service.md) |
| **Heartbeat** | 🥇 Gold | 🛡️ Resilience | Production-ready | Failure detection in distributed systems | [→](heartbeat.md) |
| **Eventual Consistency** | 🥇 Gold | 💾 Data | Production-ready | BASE over ACID for scale | [→](eventual-consistency.md) |
| **Service Discovery** | 🥇 Gold | 🏗️ Core | Production-ready | Dynamic service location | [→](service-discovery.md) |
| **Idempotent Receiver** | 🥇 Gold | 💾 Data | Production-ready | Handling duplicate messages | [→](idempotent-receiver.md) |
| **Priority Queue** | 🥇 Gold | 💾 Data | Production-ready | Task prioritization at scale | [→](priority-queue.md) |
| **Geo-Distribution** | 🥇 Gold | ⚙️ Operational | Production-ready | Global data distribution | [→](geo-distribution.md) |
| **Multi-Region** | 🥇 Gold | ⚙️ Operational | Production-ready | Geographic redundancy | [→](multi-region.md) |
| **Service Registry** | 🥇 Gold | 🏗️ Core | Production-ready | Service metadata management | [→](service-registry.md) |
| **Materialized View** | 🥇 Gold | 💾 Data | Production-ready | Precomputed query results | [→](materialized-view.md) |
| **Polyglot Persistence** | 🥇 Gold | 💾 Data | Production-ready | Right database for right job | [→](polyglot-persistence.md) |
| **Request Routing** | 🥇 Gold | ⚙️ Operational | Production-ready | Intelligent request distribution | [→](request-routing.md) |
| **Distributed Storage** | 🥇 Gold | 💾 Data | Production-ready | Scalable storage systems | [→](distributed-storage.md) |
| **Event-Driven** | 🥇 Gold | 🏗️ Core | Production-ready | Loosely coupled architectures | [→](event-driven.md) |
| **Leader Election** | 🥇 Gold | 🤝 Coordination | Production-ready | Single coordinator selection | [→](leader-election.md) |
| **Distributed Lock** | 🥇 Gold | 🤝 Coordination | Production-ready | Mutual exclusion at scale | [→](distributed-lock.md) |
| **Saga Pattern** | 🥇 Gold | 🏗️ Core | Production-ready | Distributed transactions | [→](saga.md) |
| **Event Sourcing** | 🥇 Gold | 🏗️ Core | Production-ready | Audit trail and temporal queries | [→](event-sourcing.md) |
| **Service Mesh** | 🥈 Silver | 🏗️ Core | Production-ready | Service-to-service communication | [→](service-mesh.md) |
| **Bulkhead** | 🥈 Silver | 🛡️ Resilience | Production-ready | Resource isolation | [→](bulkhead.md) |
| **Graceful Degradation** | 🥈 Silver | 🛡️ Resilience | Production-ready | Feature reduction under load | [→](graceful-degradation.md) |
| **Load Shedding** | 🥈 Silver | 🛡️ Resilience | Production-ready | Selective request dropping | [→](load-shedding.md) |
| **Backpressure** | 🥈 Silver | 🛡️ Resilience | Production-ready | Flow control in streams | [→](backpressure.md) |
| **Event Streaming** | 🥈 Silver | 💾 Data | Production-ready | Real-time data processing | [→](event-streaming.md) |
| **CDC** | 🥈 Silver | 💾 Data | Production-ready | Database change capture | [→](cdc.md) |
| **Outbox Pattern** | 🥈 Silver | 💾 Data | Production-ready | Transactional messaging | [→](outbox.md) |
| **State Watch** | 🥈 Silver | 🤝 Coordination | Production-ready | Change notifications | [→](state-watch.md) |
| **Logical Clocks** | 🥈 Silver | 🤝 Coordination | Production-ready | Event ordering | [→](logical-clocks.md) |
| **Cell-Based** | 🥈 Silver | ⚙️ Operational | Production-ready | Blast radius isolation | [→](cell-based.md) |
| **Edge Computing** | 🥈 Silver | ⚙️ Operational | Production-ready | Processing at network edge | [→](edge-computing.md) |
| **Sidecar Pattern** | 🥈 Silver | 🏗️ Core | Production-ready | Service proxy pattern | [→](sidecar.md) |
| **BFF** | 🥈 Silver | 🏗️ Core | Production-ready | Backend for Frontend | [→](backends-for-frontends.md) |
| **GraphQL Federation** | 🥈 Silver | 🏗️ Core | Production-ready | Distributed GraphQL | [→](graphql-federation.md) |
| **Lambda Architecture** | 🥈 Silver | 💾 Data | Production-ready | Batch + Stream processing | [→](lambda-architecture.md) |
| **Read Repair** | 🥈 Silver | 💾 Data | Production-ready | Consistency repair on read | [→](read-repair.md) |
| **Tunable Consistency** | 🥈 Silver | 💾 Data | Production-ready | Configurable consistency levels | [→](tunable-consistency.md) |
| **Low/High-Water Marks** | 🥈 Silver | 💾 Data | Production-ready | Flow control boundaries | [→](low-high-water-marks.md) |
| **Generation Clock** | 🥈 Silver | 🤝 Coordination | Production-ready | Epoch-based versioning | [→](generation-clock.md) |
| **Lease** | 🥈 Silver | 🤝 Coordination | Production-ready | Time-bound ownership | [→](lease.md) |
| **Clock Sync** | 🥈 Silver | 🤝 Coordination | Production-ready | Time synchronization | [→](clock-sync.md) |
| **Shared Nothing** | 🥈 Silver | 🏗️ Core | Production-ready | Complete isolation | [→](shared-nothing.md) |
| **Choreography** | 🥈 Silver | 🏗️ Core | Production-ready | Decentralized workflow | [→](choreography.md) |
| **Request Batching** | 🥈 Silver | 💾 Data | Production-ready | Reducing overhead | [→](request-batching.md) |
| **Segmented Log** | 🥈 Silver | 💾 Data | Production-ready | Log management | [→](segmented-log.md) |
| **Strangler Fig** | 🥈 Silver | ⚙️ Operational | Production-ready | Legacy system migration | [→](strangler-fig.md) |
| **Anti-Corruption Layer** | 🥈 Silver | 🏗️ Core | Production-ready | Domain isolation | [→](anti-corruption-layer.md) |
| **Scatter-Gather** | 🥈 Silver | 🏗️ Core | Production-ready | Parallel request processing | [→](scatter-gather.md) |
| **Split-Brain Resolution** | 🥈 Silver | 🛡️ Resilience | Production-ready | Network partition handling | [→](split-brain.md) |
| **HLC** | 🥈 Silver | 🤝 Coordination | Production-ready | Hybrid logical clocks | [→](hlc.md) |
| **CRDT** | 🥈 Silver | 💾 Data | Production-ready | Conflict-free data types | [→](crdt.md) |
| **Merkle Trees** | 🥈 Silver | 💾 Data | Production-ready | Efficient data verification | [→](merkle-trees.md) |
| **Bloom Filter** | 🥈 Silver | 💾 Data | Production-ready | Probabilistic set membership | [→](bloom-filter.md) |
| **Geo-Replication** | 🥈 Silver | 💾 Data | Production-ready | Geographic data replication | [→](geo-replication.md) |
| **Kappa Architecture** | 🥈 Silver | 💾 Data | Production-ready | Stream-only processing | [→](kappa-architecture.md) |
| **Fault Tolerance** | 🥈 Silver | 🛡️ Resilience | Production-ready | System resilience patterns | [→](fault-tolerance.md) |
| **Serverless/FaaS** | 🥉 Bronze | 🏗️ Core | Emerging | Event-driven compute | [→](serverless-faas.md) |
| **LSM Tree** | 🥉 Bronze | 💾 Data | Specialized | Write-optimized storage | [→](lsm-tree.md) |
| **Emergent Leader** | 🥉 Bronze | 🤝 Coordination | Specialized | Natural leader selection | [→](emergent-leader.md) |
| **Single-Socket Channel** | 🥉 Bronze | 🏗️ Core | Specialized | Connection multiplexing | [→](single-socket-channel.md) |
| **Ambassador Pattern** | 🥉 Bronze | 🏗️ Core | Specialized | Remote service proxy | [→](ambassador.md) |
| **Actor Model** | 🥉 Bronze | 🏗️ Core | Specialized | Message-based concurrency | [→](actor-model.md) |
| **WebSocket Patterns** | 🥉 Bronze | 🏗️ Core | Specialized | Real-time bidirectional | [→](websocket.md) |
| **Data Mesh** | 🥉 Bronze | 💾 Data | Emerging | Domain-oriented data | [→](data-mesh.md) |
| **Data Lake** | 🥉 Bronze | 💾 Data | Specialized | Raw data storage | [→](data-lake.md) |
| **Valet Key** | 🥉 Bronze | 🛡️ Security | Specialized | Temporary access tokens | [→](valet-key.md) |
| **CAS** | 🥉 Bronze | 🤝 Coordination | Specialized | Compare-and-swap operations | [→](cas.md) |
| **Delta Sync** | 🥉 Bronze | 💾 Data | Specialized | Efficient data synchronization | [→](delta-sync.md) |
| **Shared Database** | 🥉 Bronze | 💾 Data | Anti-pattern | Multiple services, one DB | [→](shared-database.md) |
| **Stored Procedures** | 🥉 Bronze | 🏗️ Core | Legacy | Business logic in database | [→](stored-procedures.md) |
| **Thick Client** | 🥉 Bronze | 🏗️ Core | Legacy | Heavy client-side logic | [→](thick-client.md) |
| **Singleton Database** | 🥉 Bronze | 💾 Data | Anti-pattern | Single point of failure | [→](singleton-database.md) |
| **Deduplication** | 🥉 Bronze | 💾 Data | Specialized | Removing duplicate data | [→](deduplication.md) |
| **Chunking** | 🥉 Bronze | 💾 Data | Specialized | Data partitioning | [→](chunking.md) |
| **Geohashing** | 🥉 Bronze | 💾 Data | Specialized | Spatial indexing | [→](geohashing.md) |
| **ID Generation at Scale** | 🥉 Bronze | 💾 Data | Specialized | Distributed ID generation | [→](id-generation-scale.md) |
| **Time-Series IDs** | 🥉 Bronze | 💾 Data | Specialized | Time-based identifiers | [→](time-series-ids.md) |
| **URL Normalization** | 🥉 Bronze | 💾 Data | Specialized | Canonical URL forms | [→](url-normalization.md) |
| **Tile Caching** | 🥉 Bronze | 💾 Data | Specialized | Map tile optimization | [→](tile-caching.md) |
| **Adaptive Scheduling** | 🥉 Bronze | ⚙️ Operational | Specialized | Dynamic task scheduling | [→](adaptive-scheduling.md) |
| **Analytics at Scale** | 🥉 Bronze | 💾 Data | Specialized | Big data processing | [→](analytics-scale.md) |
| **Spatial Indexing** | 🥈 Silver | 💾 Data | Production-ready | Efficient geographic queries | [→](spatial-indexing.md) |

</div>

## Pattern Statistics

<div class="pattern-stats" style="background: #f0f4f8; padding: 2rem; border-radius: 8px; margin-top: 2rem;">
    <h3>Distribution by Category</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-top: 1rem;">
        <div style="text-align: center;">
            <h4 style="margin: 0;">🏗️ Core</h4>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">28</p>
        </div>
        <div style="text-align: center;">
            <h4 style="margin: 0;">🛡️ Resilience</h4>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">14</p>
        </div>
        <div style="text-align: center;">
            <h4 style="margin: 0;">💾 Data</h4>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">40</p>
        </div>
        <div style="text-align: center;">
            <h4 style="margin: 0;">🤝 Coordination</h4>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">10</p>
        </div>
        <div style="text-align: center;">
            <h4 style="margin: 0;">⚙️ Operational</h4>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">9</p>
        </div>
    </div>
</div>

## Implementation Success Factors

| Excellence Tier | Implementation Time | Team Size | Success Rate | ROI Timeline |
|-----------------|-------------------|-----------|--------------|--------------|
| 🥇 **Gold** | 1-2 weeks | 2-3 engineers | 95% | 1-3 months |
| 🥈 **Silver** | 2-4 weeks | 3-5 engineers | 85% | 3-6 months |
| 🥉 **Bronze** | 4-8 weeks | 4-8 engineers | 70% | 6-12 months |

## Quick Links

- [Pattern Selector Tool](pattern-selector-tool.md) - Interactive decision tree
- [Excellence Guides](excellence/) - Implementation best practices
- [Pattern Health Dashboard](excellence/pattern-health-dashboard.md) - Real-time metrics
- [Case Studies](../case-studies/) - Real-world implementations

---

<div class="page-nav" markdown>
[:material-arrow-left: Pattern Index](index.md) | 
[:material-arrow-up: Home](/) | 
[:material-arrow-right: Excellence Guides](excellence/)
</div>

<script>
function filterCatalog() {
    const searchTerm = document.getElementById('catalog-search').value.toLowerCase();
    const tierFilter = document.getElementById('tier-filter').value;
    const categoryFilter = document.getElementById('category-filter').value;
    
    const rows = document.querySelectorAll('#catalog-table-container table tbody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const tierCell = row.cells[1].textContent.toLowerCase();
        const categoryCell = row.cells[2].textContent.toLowerCase();
        
        let showRow = true;
        
        // Search filter
        if (searchTerm && !text.includes(searchTerm)) {
            showRow = false;
        }
        
        // Tier filter
        if (tierFilter) {
            if (tierFilter === 'gold' && !tierCell.includes('gold')) showRow = false;
            if (tierFilter === 'silver' && !tierCell.includes('silver')) showRow = false;
            if (tierFilter === 'bronze' && !tierCell.includes('bronze')) showRow = false;
        }
        
        // Category filter
        if (categoryFilter) {
            if (categoryFilter === 'core' && !categoryCell.includes('core')) showRow = false;
            if (categoryFilter === 'resilience' && !categoryCell.includes('resilience')) showRow = false;
            if (categoryFilter === 'data' && !categoryCell.includes('data')) showRow = false;
            if (categoryFilter === 'coordination' && !categoryCell.includes('coordination')) showRow = false;
            if (categoryFilter === 'operational' && !categoryCell.includes('operational')) showRow = false;
        }
        
        row.style.display = showRow ? '' : 'none';
    });
    
    updateCatalogStats();
}

function updateCatalogStats() {
    const visibleRows = document.querySelectorAll('#catalog-table-container table tbody tr:not([style*="display: none"])');
    console.log(`Showing ${visibleRows.length} patterns`);
}

function exportCatalog() {
    const rows = document.querySelectorAll('#catalog-table-container table tbody tr:not([style*="display: none"])');
    let csv = 'Pattern,Tier,Category,Status,Use When\n';
    
    rows.forEach(row => {
        const cells = row.cells;
        csv += `"${cells[0].textContent}","${cells[1].textContent}","${cells[2].textContent}","${cells[3].textContent}","${cells[4].textContent}"\n`;
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'pattern-catalog.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}
</script>