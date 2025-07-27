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
| **Service Mesh** | 🥈 Silver | 🏗️ Core | Large | Istio, Linkerd | Service communication | [→](service-mesh.md) |
| **Event-Driven** | 🥈 Silver | 🏗️ Core | Medium+ | Uber, Lyft | Loose coupling | [→](event-driven.md) |
| **Event Sourcing** | 🥈 Silver | 🏗️ Core | Large | Banking, FinTech | Audit trail | [→](event-sourcing.md) |
| **Saga Pattern** | 🥈 Silver | 🏗️ Core | Large | Booking.com, Uber | Distributed transactions | [→](saga.md) |
| **Bulkhead** | 🥈 Silver | 🛡️ Resilience | Medium+ | Netflix (Hystrix) | Resource isolation | [→](bulkhead.md) |
| **Graceful Degradation** | 🥈 Silver | 🛡️ Resilience | Medium+ | Netflix, Amazon | Feature reduction | [→](graceful-degradation.md) |
| **Load Shedding** | 🥈 Silver | 🛡️ Resilience | Large | Google, Facebook | Overload protection | [→](load-shedding.md) |
| **Backpressure** | 🥈 Silver | 🛡️ Resilience | Medium+ | Reactive systems | Flow control | [→](backpressure.md) |
| **Event Streaming** | 🥈 Silver | 💾 Data | Large | LinkedIn (Kafka) | Real-time processing | [→](event-streaming.md) |
| **CDC** | 🥈 Silver | 💾 Data | Large | Debezium users | Change capture | [→](cdc.md) |
| **Outbox Pattern** | 🥈 Silver | 💾 Data | Medium+ | E-commerce | Transactional messaging | [→](outbox.md) |
| **Distributed Lock** | 🥈 Silver | 🤝 Coordination | Medium+ | Redis, Zookeeper | Mutual exclusion | [→](distributed-lock.md) |
| **Leader Election** | 🥈 Silver | 🤝 Coordination | Medium+ | Kubernetes, Consul | Single writer | [→](leader-election.md) |
| **State Watch** | 🥈 Silver | 🤝 Coordination | Medium+ | etcd, Zookeeper | Change notification | [→](state-watch.md) |
| **Logical Clocks** | 🥈 Silver | 🤝 Coordination | Large | Distributed DBs | Event ordering | [→](logical-clocks.md) |
| **Multi-Region** | 🥈 Silver | ⚙️ Operational | Large | Netflix, Spotify | Geographic distribution | [→](multi-region.md) |
| **Cell-Based** | 🥈 Silver | ⚙️ Operational | Large | AWS, Slack | Blast radius control | [→](cell-based.md) |
| **Edge Computing** | 🥈 Silver | ⚙️ Operational | Large | CloudFlare Workers | Process at edge | [→](edge-computing.md) |
| **Service Registry** | 🥈 Silver | 🏗️ Core | Medium+ | Consul, Eureka | Service discovery | [→](service-registry.md) |
| **Sidecar Pattern** | 🥈 Silver | 🏗️ Core | Medium+ | Envoy, Linkerd | Proxy pattern | [→](sidecar.md) |
| **BFF** | 🥈 Silver | 🏗️ Core | Medium+ | Netflix, SoundCloud | Backend for Frontend | [→](backends-for-frontends.md) |
| **GraphQL Federation** | 🥈 Silver | 🏗️ Core | Large | Apollo, Netflix | Distributed GraphQL | [→](graphql-federation.md) |
| **Lambda Architecture** | 🥈 Silver | 💾 Data | Large | LinkedIn, Twitter | Batch + Stream | [→](lambda-architecture.md) |
| **Materialized View** | 🥈 Silver | 💾 Data | Medium+ | PostgreSQL, Oracle | Precomputed results | [→](materialized-view.md) |
| **Read Repair** | 🥈 Silver | 💾 Data | Large | Cassandra, Riak | Consistency repair | [→](read-repair.md) |
| **Tunable Consistency** | 🥈 Silver | 💾 Data | Large | Cassandra, DynamoDB | Configurable consistency | [→](tunable-consistency.md) |
| **Low/High-Water Marks** | 🥈 Silver | 💾 Data | Medium+ | Kafka, DBs | Flow control | [→](low-high-water-marks.md) |
| **Generation Clock** | 🥈 Silver | 🤝 Coordination | Medium+ | Distributed systems | Epoch tracking | [→](generation-clock.md) |
| **Lease** | 🥈 Silver | 🤝 Coordination | Medium+ | HDFS, GFS | Time-bound ownership | [→](lease.md) |
| **Clock Sync** | 🥈 Silver | 🤝 Coordination | Large | Google Spanner | Time synchronization | [→](clock-sync.md) |
| **Heartbeat** | 🥈 Silver | 🛡️ Resilience | All | All distributed systems | Failure detection | [→](heartbeat.md) |
| **Eventual Consistency** | 🥈 Silver | 💾 Data | Large | NoSQL databases | Convergence guarantee | [→](eventual-consistency.md) |
| **Shared Nothing** | 🥈 Silver | 🏗️ Core | Large | MPP databases | Complete isolation | [→](shared-nothing.md) |
| **Observability Stack** | 🥈 Silver | ⚙️ Operational | Medium+ | Modern platforms | Full visibility | [→](observability.md) |
| **Polyglot Persistence** | 🥈 Silver | 💾 Data | Large | Microservices | Multiple databases | [→](polyglot-persistence.md) |
| **Request Routing** | 🥈 Silver | ⚙️ Operational | Medium+ | Load balancers | Smart routing | [→](request-routing.md) |
| **Choreography** | 🥈 Silver | 🏗️ Core | Large | Event-driven systems | Decentralized workflow | [→](choreography.md) |
| **Serverless/FaaS** | 🥉 Bronze | 🏗️ Core | Variable | AWS Lambda | Pay per use | [→](serverless-faas.md) |
| **Request Batching** | 🥉 Bronze | 💾 Data | Medium+ | GraphQL, DBs | Reduce overhead | [→](request-batching.md) |
| **LSM Tree** | 🥉 Bronze | 💾 Data | Large | RocksDB, Cassandra | Write optimization | [→](lsm-tree.md) |
| **Segmented Log** | 🥉 Bronze | 💾 Data | Medium+ | Kafka, DBs | Log management | [→](segmented-log.md) |
| **Distributed Storage** | 🥉 Bronze | 💾 Data | Large | HDFS, Ceph | Multi-node storage | [→](distributed-storage.md) |
| **Emergent Leader** | 🥉 Bronze | 🤝 Coordination | Medium+ | Gossip systems | Natural selection | [→](emergent-leader.md) |
| **Single-Socket Channel** | 🥉 Bronze | 🏗️ Core | Small | Custom protocols | Connection reuse | [→](single-socket-channel.md) |
| **Ambassador Pattern** | 🥉 Bronze | 🏗️ Core | Medium | Kubernetes | Remote proxy | [→](ambassador.md) |
| **Actor Model** | 🥉 Bronze | 🏗️ Core | Medium | Erlang, Akka | Message passing | [→](actor-model.md) |
| **WebSocket Patterns** | 🥉 Bronze | 🏗️ Core | Medium | Real-time apps | Bidirectional comm | [→](websocket.md) |
| **Data Mesh** | 🥉 Bronze | 💾 Data | Large | ThoughtWorks | Domain-oriented data | [→](data-mesh.md) |
| **Kappa Architecture** | 🥉 Bronze | 💾 Data | Large | Stream-only systems | Simplified Lambda | [→](kappa-architecture.md) |
| **Data Lake** | 🥉 Bronze | 💾 Data | Large | Big data platforms | Raw storage | [→](data-lake.md) |
| **Valet Key** | 🥉 Bronze | 🛡️ Security | Medium | Cloud storage | Temporary access | [→](valet-key.md) |
| **TCC** | 🥉 Bronze | 💾 Data | Medium | Business systems | Try-Confirm-Cancel | [→](tcc.md) |
| **Idempotent Receiver** | 🥉 Bronze | 💾 Data | Medium | Message systems | Duplicate handling | [→](idempotent-receiver.md) |
| **CAS** | 🥉 Bronze | 🤝 Coordination | Medium | Atomic operations | Compare and swap | [→](cas.md) |
| **Gossip Protocol** | 🥉 Bronze | 🤝 Coordination | Large | Cassandra, Consul | Information spread | [→](gossip-protocol.md) |
| **Anti-Entropy** | 🥉 Bronze | 💾 Data | Large | Eventually consistent | Repair divergence | [→](anti-entropy.md) |
| **CRDTs** | 🥉 Bronze | 💾 Data | Large | Collaborative apps | Conflict-free merge | [→](crdt.md) |
| **Merkle Trees** | 🥉 Bronze | 💾 Data | Large | Git, Blockchain | Efficient comparison | [→](merkle-trees.md) |
| **Bloom Filter** | 🥉 Bronze | 💾 Data | Large | Databases, Caches | Set membership | [→](bloom-filter.md) |
| **B-Tree** | 🥉 Bronze | 💾 Data | All | Databases | Ordered storage | [→](btree.md) |
| **PBFT** | 🥉 Bronze | 🤝 Coordination | Small | Blockchain | Byzantine tolerance | [→](pbft.md) |
| **Delta Sync** | 🥉 Bronze | 💾 Data | Medium | Mobile apps | Efficient sync | [→](delta-sync.md) |
| **Compression Patterns** | 🥉 Bronze | ⚙️ Operational | All | Network systems | Bandwidth saving | [→](compression.md) |
| **Protocol Buffers** | 🥉 Bronze | 🏗️ Core | Medium+ | gRPC, Google | Efficient serialization | [→](protobuf.md) |
| **RPC Patterns** | 🥉 Bronze | 🏗️ Core | All | Microservices | Remote calls | [→](rpc.md) |
| **Scheduler Patterns** | 🥉 Bronze | ⚙️ Operational | Large | Kubernetes, Mesos | Resource allocation | [→](scheduler.md) |
| **Split-Brain Resolution** | 🥉 Bronze | 🛡️ Resilience | Medium+ | Clustered systems | Partition handling | [→](split-brain.md) |
| **Cache Aside** | 🥉 Bronze | 💾 Data | All | Application caches | Lazy loading | [→](cache-aside.md) |
| **Read-Through Cache** | 🥉 Bronze | 💾 Data | Medium | ORM systems | Transparent caching | [→](read-through-cache.md) |
| **Write-Through Cache** | 🥉 Bronze | 💾 Data | Medium | Database caches | Sync writes | [→](write-through-cache.md) |
| **Write-Behind Cache** | 🥉 Bronze | 💾 Data | Large | High-write systems | Async writes | [→](write-behind-cache.md) |
| **Shared Database** | 🥉 Bronze | 💾 Data | Small | Legacy systems | Anti-pattern | [→](shared-database.md) |
| **Stored Procedures** | 🥉 Bronze | 🏗️ Core | Small | Legacy databases | Business in DB | [→](stored-procedures.md) |
| **Thick Client** | 🥉 Bronze | 🏗️ Core | Small | Desktop apps | Fat client anti-pattern | [→](thick-client.md) |
| **Singleton Database** | 🥉 Bronze | 💾 Data | Small | Legacy monoliths | Single DB anti-pattern | [→](singleton-database.md) |
| **Database per Service** | 🥇 Gold | 💾 Data | Medium+ | Microservices | Service autonomy | [→](database-per-service.md) |

</div>

## Pattern Statistics

<div class="pattern-stats" style="background: #f0f4f8; padding: 2rem; border-radius: 8px; margin-top: 2rem;">
    <h3>Distribution by Category</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-top: 1rem;">
        <div style="text-align: center;">
            <h4 style="margin: 0;">🏗️ Core</h4>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">22</p>
        </div>
        <div style="text-align: center;">
            <h4 style="margin: 0;">🛡️ Resilience</h4>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">15</p>
        </div>
        <div style="text-align: center;">
            <h4 style="margin: 0;">💾 Data</h4>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">35</p>
        </div>
        <div style="text-align: center;">
            <h4 style="margin: 0;">🤝 Coordination</h4>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">12</p>
        </div>
        <div style="text-align: center;">
            <h4 style="margin: 0;">⚙️ Operational</h4>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">11</p>
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
    let csv = 'Pattern,Tier,Category,Scale,Companies Using,Key Benefit\n';
    
    rows.forEach(row => {
        const cells = row.cells;
        csv += `"${cells[0].textContent}","${cells[1].textContent}","${cells[2].textContent}","${cells[3].textContent}","${cells[4].textContent}","${cells[5].textContent}"\n`;
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