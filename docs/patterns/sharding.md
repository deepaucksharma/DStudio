---
title: Sharding (Data Partitioning)
description: Horizontally partition data across multiple databases to improve scalability and performance
type: pattern
category: distributed-data
difficulty: advanced
reading_time: 30 min
prerequisites: [database-design, distributed-systems, consistency-models, hashing]
when_to_use: Dataset exceeds single server capacity, need horizontal scaling, multi-tenant applications, geographic data distribution, high write throughput requirements, isolation between data subsets
when_not_to_use: Complex cross-shard queries needed, strong consistency requirements across shards, small datasets, high operational complexity not justified, frequent resharding expected
status: complete
last_updated: 2025-07-21
tags: [scalability, partitioning, horizontal-scaling, data-distribution, multi-tenancy, sharding-strategies]
excellence_tier: gold
pattern_status: recommended
introduced: 2000-01
current_relevance: mainstream
modern_examples:
  - company: Discord
    implementation: "MongoDB sharding for messages and guild data"
    scale: "150M+ users, 1T+ messages across thousands of shards"
  - company: Pinterest
    implementation: "MySQL sharding for user data and pins"
    scale: "450M+ users, 240B+ pins saved"
  - company: Facebook
    implementation: "Custom sharding across thousands of MySQL instances"
    scale: "3B+ users, exabytes of data"
production_checklist:
  - "Choose sharding key based on access patterns (user_id, tenant_id)"
  - "Implement shard routing layer (Vitess, ProxySQL, custom)"
  - "Plan for resharding from day one (consistent hashing helps)"
  - "Monitor shard distribution and rebalance hot shards"
  - "Handle cross-shard queries carefully (avoid when possible)"
  - "Implement proper backup strategy per shard"
  - "Use shard replicas for high availability"
  - "Test shard failure scenarios and recovery"
---

# Sharding (Data Partitioning)

!!! success "🏆 Gold Standard Pattern"
    **Horizontal Scaling Foundation** • Discord, Pinterest, Facebook at planet scale
    
    Sharding is the fundamental pattern for scaling databases beyond single-machine limits. It enables linear scaling by distributing data across multiple machines based on a partition key.
    
    **Key Success Metrics:**
    - Discord: 1T+ messages across thousands of shards
    - Pinterest: 240B+ pins distributed globally
    - Facebook: 3B+ users, exabytes of data

[Home](/) > [Patterns](patterns) > [Data Patterns](patterns/#data-patterns) > Sharding

**Divide and conquer at planetary scale - How to handle 100B+ records**

> *"The only way to handle infinite data is to ensure no single place has to handle all of it."*

!!! abstract "Pattern Overview"
    **Problem**: Single database hitting limits (100TB data, 50K writes/sec)  
    **Solution**: Horizontally partition data across multiple independent databases  
    **Trade-offs**: Complexity for scalability, eventual consistency for performance  
    **Used by**: Instagram (Cassandra - 100+ nodes), Discord (MongoDB - 1T+ messages), Uber (MySQL - 1000+ shards)

---

## Level 1: Intuition

### The Problem at Scale

| Single Database Limits | With Sharding |
|------------------------|---------------|
| **Storage**: 100TB max | **Storage**: Unlimited (add shards) |
| **Writes**: 50K/sec ceiling | **Writes**: 1M+/sec (parallel writes) |
| **Reads**: 100K/sec max | **Reads**: 10M+/sec (parallel reads) |
| **Growth**: Vertical only | **Growth**: Horizontal scaling |

```
Unsharded (Before):              Sharded (After):
┌─────────────────────┐         ┌──────────┐ ┌──────────┐ ┌──────────┐
│   MySQL Primary     │         │ Shard 0  │ │ Shard 1  │ │ Shard 2  │
│   100M users       │   →     │ 33M users│ │ 33M users│ │ 34M users│
│   CPU: 95%         │         │ CPU: 30% │ │ CPU: 32% │ │ CPU: 31% │
│   Latency: 500ms   │         │ <50ms    │ │ <50ms    │ │ <50ms    │
└─────────────────────┘         └──────────┘ └──────────┘ └──────────┘
    🔥 On fire!                    😊 Smooth operation
```

### Sharding Architecture Overview

```mermaid
graph TB
    subgraph "Application Layer"
        APP[Application]
        ROUTER[Shard Router]
    end
    
    subgraph "Sharding Logic"
        HASH[Hash Function]
        MAP[Shard Mapping]
    end
    
    subgraph "Data Shards"
        S0[(Shard 0<br/>Users A-F)]
        S1[(Shard 1<br/>Users G-M)]
        S2[(Shard 2<br/>Users N-S)]
        S3[(Shard 3<br/>Users T-Z)]
    end
    
    APP --> ROUTER
    ROUTER --> HASH
    HASH --> MAP
    MAP --> S0
    MAP --> S1
    MAP --> S2
    MAP --> S3
    
    style ROUTER fill:#ffd,stroke:#333,stroke-width:2px
    style S0 fill:#9f6,stroke:#333,stroke-width:2px
    style S1 fill:#9f6,stroke:#333,stroke-width:2px
    style S2 fill:#9f6,stroke:#333,stroke-width:2px
    style S3 fill:#9f6,stroke:#333,stroke-width:2px
```

### Sharding Request Flow

```mermaid
flowchart LR
    REQ[Request: Get User 123] --> ROUTE{Router}
    ROUTE --> CALC[Calculate: hash(123) % 4 = 2]
    CALC --> SHARD[Connect to Shard 2]
    SHARD --> QUERY[Execute Query]
    QUERY --> RESULT[Return Data]
    
    style ROUTE fill:#ffd,stroke:#333,stroke-width:2px
    style SHARD fill:#9f6,stroke:#333,stroke-width:2px
```

---

## Level 2: Foundation

### Critical Decision: Choosing Your Sharding Strategy

!!! warning "The Most Important Architecture Decision"
    Your sharding strategy determines:
    - **Query patterns** you can support efficiently
    - **Scaling characteristics** as you grow
    - **Operational complexity** for your team
    - **Migration difficulty** if you need to change

#### Strategy Comparison Matrix

| Strategy | Distribution | Query Support | Resharding | Use Case |
|----------|--------------|---------------|------------|----------|
| **Range-Based** | Can be uneven | Range queries ✓ | Hard | Time-series data |
| **Hash-Based** | Even | Point queries only | Very hard | User data |
| **Directory** | Flexible | Any query | Easy | Multi-tenant |
| **Geo-Based** | By location | Location queries | Medium | CDN, regional data |
| **Composite** | Custom | Depends | Complex | Enterprise systems |

=== "Range-Based Sharding"

    ```python
    # Range-based sharding implementation
    class RangeShardRouter:
        def __init__(self):
            self.ranges = [
                (0, 999, 'shard_0'),
                (1000, 1999, 'shard_1'),
                (2000, 2999, 'shard_2'),
                (3000, 3999, 'shard_3')
            ]
        
        def get_shard(self, key: int) -> str:
            for start, end, shard in self.ranges:
                if start <= key <= end:
                    return shard
            raise ValueError(f"No shard found for key: {key}")
    
    # Example usage
    router = RangeShardRouter()
    print(router.get_shard(1500))  # Returns: shard_1
    ```
    
    **Pros**:
    - Simple to implement and understand
    - Supports efficient range queries
    - Natural ordering preserved
    - Easy to query sequential data
    
    **Cons**:
    - Can create hotspots (uneven distribution)
    - Difficult to rebalance
    - Sequential IDs cluster on same shard
    - May need manual range adjustments
    
    **Best For**:
    - Time-series data (date ranges)
    - Sequential IDs with predictable growth
    - Applications needing range scans
    - Log data with timestamps

=== "Hash-Based Sharding"

    ```python
    # Hash-based sharding implementation
    import hashlib
    
    class HashShardRouter:
        def __init__(self, shard_count: int = 4):
            self.shard_count = shard_count
            self.shards = [f'shard_{i}' for i in range(shard_count)]
        
        def get_shard(self, key: str) -> str:
            # Use consistent hashing for even distribution
            hash_value = hashlib.md5(key.encode()).hexdigest()
            shard_index = int(hash_value, 16) % self.shard_count
            return self.shards[shard_index]
        
        def consistent_hash(self, key: str, virtual_nodes: int = 150) -> str:
            # More advanced: consistent hashing with virtual nodes
            ring = {}
            for i in range(self.shard_count):
                for vn in range(virtual_nodes):
                    vnode_key = f"{self.shards[i]}:{vn}"
                    hash_val = int(hashlib.md5(vnode_key.encode()).hexdigest(), 16)
                    ring[hash_val] = self.shards[i]
            
            key_hash = int(hashlib.md5(key.encode()).hexdigest(), 16)
            for node_hash in sorted(ring.keys()):
                if key_hash <= node_hash:
                    return ring[node_hash]
            return ring[sorted(ring.keys())[0]]
    
    # Example usage
    router = HashShardRouter(4)
    print(router.get_shard("user123"))  # Evenly distributed
    ```
    
    **Pros**:
    - Even data distribution
    - No hotspots from sequential keys
    - Predictable performance
    - Works well with random keys
    
    **Cons**:
    - No efficient range queries
    - Related data scattered across shards
    - Resharding requires rehashing
    - Lost data locality
    
    **Best For**:
    - User data with UUID/random IDs
    - Session storage
    - Cache systems
    - High-write workloads

=== "Geographic Sharding"

    ```python
    # Geographic sharding implementation
    class GeoShardRouter:
        def __init__(self):
            self.region_map = {
                'US': ['us-east-1', 'us-west-2'],
                'EU': ['eu-west-1', 'eu-central-1'],
                'ASIA': ['ap-south-1', 'ap-northeast-1'],
                'DEFAULT': ['global-1']
            }
            self.ip_ranges = {
                '1.0.0.0/8': 'ASIA',
                '2.0.0.0/8': 'EU',
                '3.0.0.0/8': 'US',
            }
        
        def get_shard_by_location(self, user_ip: str, user_region: str = None) -> str:
            # Prefer explicit region
            if user_region and user_region in self.region_map:
                shards = self.region_map[user_region]
                return self.select_least_loaded(shards)
            
            # Fall back to IP geolocation
            region = self.get_region_from_ip(user_ip)
            shards = self.region_map.get(region, self.region_map['DEFAULT'])
            return self.select_least_loaded(shards)
        
        def get_region_from_ip(self, ip: str) -> str:
            # Simplified IP to region mapping
            for ip_range, region in self.ip_ranges.items():
                if self.ip_in_range(ip, ip_range):
                    return region
            return 'DEFAULT'
    
    # Example usage
    router = GeoShardRouter()
    print(router.get_shard_by_location('3.14.15.92'))  # US shard
    ```
    
    **Pros**:
    - Data locality (lower latency)
    - Compliance with data residency laws
    - Natural disaster isolation
    - Follows user distribution
    
    **Cons**:
    - Complex cross-region queries
    - Uneven distribution by region
    - Requires geo-detection
    - Higher operational complexity
    
    **Best For**:
    - Global applications
    - Content delivery networks
    - Compliance-heavy industries
    - Region-specific services

=== "Directory-Based Sharding"

    ```python
    # Directory-based sharding implementation
    class DirectoryShardRouter:
        def __init__(self):
            # Metadata store tracks key-to-shard mappings
            self.directory = {}  # In production: distributed KV store
            self.shard_stats = {}  # Track shard utilization
            
        def assign_shard(self, key: str) -> str:
            # Check if already assigned
            if key in self.directory:
                return self.directory[key]
            
            # Find least loaded shard
            shard = self.find_optimal_shard()
            self.directory[key] = shard
            self.update_stats(shard, 'add')
            return shard
        
        def get_shard(self, key: str) -> str:
            if key not in self.directory:
                return self.assign_shard(key)
            return self.directory[key]
        
        def migrate_key(self, key: str, target_shard: str):
            # Support for dynamic resharding
            old_shard = self.directory.get(key)
            if old_shard:
                self.update_stats(old_shard, 'remove')
            
            self.directory[key] = target_shard
            self.update_stats(target_shard, 'add')
        
        def find_optimal_shard(self) -> str:
            # Return shard with lowest utilization
            return min(self.shard_stats.items(), 
                      key=lambda x: x[1]['count'])[0]
    
    # Example usage
    router = DirectoryShardRouter()
    router.assign_shard("user:123")  # Dynamically assigned
    ```
    
    **Pros**:
    - Maximum flexibility
    - Easy resharding
    - Can optimize placement
    - Supports any key type
    
    **Cons**:
    - Additional lookup overhead
    - Directory becomes bottleneck
    - Requires consistent metadata store
    - More complex architecture
    
    **Best For**:
    - Dynamic workloads
    - Tenant-based sharding
    - Uneven data sizes
    - Systems needing rebalancing

=== "Composite Sharding"

    ```python
    # Composite sharding (multi-dimensional)
    class CompositeShardRouter:
        def __init__(self):
            self.dimensions = {
                'tenant': 4,      # 4 tenant shards
                'time': 12,       # 12 monthly shards
                'type': 3         # 3 data type shards
            }
            self.total_shards = 4 * 12 * 3  # 144 shards
        
        def get_shard(self, tenant_id: str, timestamp: int, 
                     data_type: str) -> str:
            # Hash tenant for distribution
            tenant_shard = hash(tenant_id) % self.dimensions['tenant']
            
            # Extract month from timestamp
            from datetime import datetime
            dt = datetime.fromtimestamp(timestamp)
            time_shard = dt.month - 1  # 0-11
            
            # Map data type to shard
            type_map = {'user': 0, 'order': 1, 'product': 2}
            type_shard = type_map.get(data_type, 0)
            
            # Combine dimensions into single shard ID
            shard_id = (tenant_shard * 12 * 3 + 
                       time_shard * 3 + 
                       type_shard)
            
            return f'shard_{shard_id}'
        
        def get_shards_for_query(self, tenant_id: str = None,
                                time_range: tuple = None,
                                data_types: list = None) -> list:
            # Return all shards that might contain matching data
            shards = []
            
            tenant_shards = [hash(tenant_id) % self.dimensions['tenant']] if tenant_id else range(4)
            time_shards = self.get_time_shards(time_range) if time_range else range(12)
            type_shards = [self.get_type_shard(dt) for dt in data_types] if data_types else range(3)
            
            for t in tenant_shards:
                for tm in time_shards:
                    for tp in type_shards:
                        shard_id = t * 12 * 3 + tm * 3 + tp
                        shards.append(f'shard_{shard_id}')
            
            return shards
    
    # Example usage
    router = CompositeShardRouter()
    shard = router.get_shard('tenant123', 1634567890, 'order')
    print(f"Data goes to: {shard}")
    
    # Query across multiple dimensions
    query_shards = router.get_shards_for_query(
        tenant_id='tenant123',
        time_range=(1633017600, 1635695999),  # Oct 2021
        data_types=['order', 'user']
    )
    print(f"Query spans {len(query_shards)} shards")
    ```
    
    **Pros**:
    - Fine-grained data distribution
    - Efficient multi-dimensional queries
    - Natural partitioning boundaries
    - Supports complex access patterns
    
    **Cons**:
    - Complex routing logic
    - Many shards to manage
    - Difficult to rebalance
    - Query complexity increases
    
    **Best For**:
    - Multi-tenant SaaS applications
    - Time-series with multiple dimensions
    - Analytics workloads
    - Systems with clear partitioning axes


### Sharding Strategy Visualizations

#### Range-Based Sharding
```mermaid
graph LR
    subgraph "Key Space"
        K1[Keys 0-999]
        K2[Keys 1000-1999]
        K3[Keys 2000-2999]
        K4[Keys 3000-3999]
    end
    
    subgraph "Shards"
        S0[(Shard 0)]
        S1[(Shard 1)]
        S2[(Shard 2)]
        S3[(Shard 3)]
    end
    
    K1 --> S0
    K2 --> S1
    K3 --> S2
    K4 --> S3
    
    style K1 fill:#ffd,stroke:#333,stroke-width:2px
    style K2 fill:#ffd,stroke:#333,stroke-width:2px
    style K3 fill:#ffd,stroke:#333,stroke-width:2px
    style K4 fill:#ffd,stroke:#333,stroke-width:2px
```

#### Consistent Hash Ring
```mermaid
graph TB
    subgraph "Hash Ring"
        R((Ring))
        N0[Node 0<br/>+ Virtual Nodes]
        N1[Node 1<br/>+ Virtual Nodes]
        N2[Node 2<br/>+ Virtual Nodes]
        N3[Node 3<br/>+ Virtual Nodes]
    end
    
    R --> N0
    R --> N1
    R --> N2
    R --> N3
    
    K1[Key: user123] -.->|hash| R
    K2[Key: order456] -.->|hash| R
    
    style R fill:#9f6,stroke:#333,stroke-width:4px
```

#### Geographic Sharding
```mermaid
graph TB
    subgraph "Regions"
        NA[North America]
        EU[Europe]
        AS[Asia]
        OT[Other]
    end
    
    subgraph "Data Centers"
        DC1[(US-East Shard)]
        DC2[(EU-West Shard)]
        DC3[(Asia-Pacific Shard)]
        DC4[(Global Shard)]
    end
    
    NA --> DC1
    EU --> DC2
    AS --> DC3
    OT --> DC4
    
    U1[US User] -.-> NA
    U2[UK User] -.-> EU
    U3[Japan User] -.-> AS
```

### Sharding Strategy Comparison

| Strategy | Distribution | Query Complexity | Rebalancing | Best For |
|----------|--------------|------------------|-------------|----------|
| **Range** | Can be uneven | Simple range queries | Hard | Sequential IDs |
| **Hash** | Even | No range queries | Hard | Random access |
| **Geographic** | By location | Region-aware | Natural | Global apps |
| **Composite** | Multi-dimensional | Complex | Flexible | Multi-tenant |
| **Directory** | Flexible | Extra lookup | Easy | Dynamic data |


### Cross-Shard Query Patterns

```mermaid
sequenceDiagram
    participant App as Application
    participant QE as Query Executor
    participant S0 as Shard 0
    participant S1 as Shard 1
    participant S2 as Shard 2
    participant S3 as Shard 3
    
    App->>QE: Get top 10 users globally
    
    par Parallel Execution
        QE->>S0: SELECT TOP 20
        QE->>S1: SELECT TOP 20
        QE->>S2: SELECT TOP 20
        QE->>S3: SELECT TOP 20
    end
    
    S0-->>QE: 20 users
    S1-->>QE: 20 users
    S2-->>QE: 20 users
    S3-->>QE: 20 users
    
    QE->>QE: Merge & Sort 80 users
    QE->>QE: Take top 10
    QE-->>App: Final top 10 users
```

### Cross-Shard Query Types

| Query Type | Pattern | Performance Impact | Example |
|------------|---------|-------------------|----------|
| **Scatter-Gather** | Query all shards | O(n) shards | Global search |
| **Targeted Multi-Shard** | Query subset | O(k) shards | Region-specific |
| **Fan-out Aggregation** | Parallel aggregates | Network bound | SUM, COUNT |
| **Sorted Merge** | Order across shards | Memory intensive | Top-K queries |
| **Two-Phase Query** | Locate then fetch | 2x latency | Secondary index |


```mermaid
graph TB
    subgraph "Query Patterns"
        Q[Cross-Shard Query]
        
        Q --> SG[Scatter-Gather<br/>All shards]
        Q --> TM[Targeted Multi<br/>Specific shards]
        Q --> FA[Fan-out<br/>Aggregation]
        Q --> SM[Sorted Merge<br/>Ordering]
    end
    
    style Q fill:#ffd,stroke:#333,stroke-width:2px
```

---

## Level 3: Deep Dive

### Advanced Sharding Patterns

#### 1. Dynamic Resharding
```python
class DynamicResharding:
    """Handle shard splits and migrations"""
    
    def __init__(self, config_store):
        self.config_store = config_store
        self.migration_lock = asyncio.Lock()
        
    async def split_shard(
        self, 
        source_shard_id: int, 
        target_shard_ids: List[int]
    ):
        """Split one shard into multiple shards"""
        async with self.migration_lock:
# Phase 1: Prepare
            migration_id = self._create_migration_record(
                source_shard_id, target_shard_ids
            )
            
# Phase 2: Dual writes
            await self._enable_dual_writes(
                source_shard_id, target_shard_ids
            )
            
# Phase 3: Backfill historical data
            await self._backfill_data(
                source_shard_id, target_shard_ids, migration_id
            )
            
# Phase 4: Verify consistency
            consistent = await self._verify_consistency(
                source_shard_id, target_shard_ids
            )
            
            if not consistent:
                await self._rollback_migration(migration_id)
                raise Exception("Migration consistency check failed")
            
# Phase 5-7: Switch, disable, cleanup
            await self._switch_reads(target_shard_ids)
            await self._disable_shard(source_shard_id)
            await self._cleanup_old_shard(source_shard_id)
    
    async def _backfill_data(
        self, 
        source_id: int, 
        target_ids: List[int],
        migration_id: str
    ):
        """Migrate data from source to targets"""
        source_conn = self.get_shard_connection(source_id)
        cursor = source_conn.cursor('migration_cursor')
        cursor.execute("""
            SELECT * FROM users 
            WHERE NOT EXISTS (
                SELECT 1 FROM migration_log 
                WHERE migration_id = %s 
                AND record_id = users.id
            )
        """, (migration_id,))
        
        batch_size = 1000
        batch = []
        
        for row in cursor:
            target_id = self._get_target_shard(row['id'], target_ids)
            batch.append((target_id, row))
            
            if len(batch) >= batch_size:
                await self._write_batch(batch, migration_id)
                batch = []
        
        if batch:
            await self._write_batch(batch, migration_id)
    
    async def _write_batch(self, batch: List[tuple], migration_id: str):
        """Write batch of records to target shards"""
        
# Group by target shard
        by_shard = defaultdict(list)
        for target_id, row in batch:
            by_shard[target_id].append(row)
        
# Write to each shard in parallel
        tasks = []
        for target_id, rows in by_shard.items():
            task = self._write_to_shard(target_id, rows, migration_id)
            tasks.append(task)
        
        await asyncio.gather(*tasks)
```

#### 2. Shard-Aware Caching
```python
class ShardAwareCache:
    """Cache that understands sharding"""
    
    def __init__(self, shard_router, cache_backend):
        self.router = shard_router
        self.cache = cache_backend
        self.local_cache = {}  # L1 cache per shard
        
    async def get(self, key: str) -> Optional[Any]:
        """Get with shard-aware caching"""
        shard_id = self.router.get_shard_id(key)
        cache_key = f"shard:{shard_id}:key:{key}"
        
# Check L1 cache
        if cache_key in self.local_cache:
            return self.local_cache[cache_key]
        
# Check L2 cache
        value = await self.cache.get(cache_key)
        if value is not None:
            self.local_cache[cache_key] = value
            return value
        
# Cache miss - fetch from shard
        shard_conn = self.router.get_connection(key)
        value = await self._fetch_from_shard(shard_conn, key)
        
        if value is not None:
            await self.cache.set(cache_key, value, ttl=300)
            self.local_cache[cache_key] = value
        
        return value
    
    async def invalidate_shard(self, shard_id: int):
        """Invalidate all cache entries for a shard"""
        
# Clear L1 cache for this shard
        keys_to_remove = [
            k for k in self.local_cache 
            if k.startswith(f"shard:{shard_id}:")
        ]
        for key in keys_to_remove:
            del self.local_cache[key]
        
# Clear L2 cache
        await self.cache.delete_pattern(f"shard:{shard_id}:*")
```

#### 3. Global Secondary Indexes
```python
class GlobalSecondaryIndex:
    """Maintain global indexes across shards"""
    
    def __init__(self, index_name: str, shard_router):
        self.index_name = index_name
        self.router = shard_router
        self.index_shards = {}  # Separate shards for index
        
    async def update_index(
        self, 
        indexed_value: Any, 
        primary_key: str,
        shard_id: int
    ):
        """Update global secondary index"""
        
# Determine which index shard handles this value
        index_shard_id = self._get_index_shard(indexed_value)
        
# Store mapping: indexed_value -> (primary_key, data_shard_id)
        index_conn = self.get_index_connection(index_shard_id)
        
        await index_conn.execute("""
            INSERT INTO {index_name}_index 
                (indexed_value, primary_key, data_shard_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (indexed_value, primary_key) 
            DO UPDATE SET data_shard_id = EXCLUDED.data_shard_id
        """.format(index_name=self.index_name), 
            (indexed_value, primary_key, shard_id)
        )
    
    async def query_by_index(
        self, 
        indexed_value: Any
    ) -> List[Dict]:
        """Query using global secondary index"""
        
# Step 1: Look up in index to find which shards have data
        index_shard_id = self._get_index_shard(indexed_value)
        index_conn = self.get_index_connection(index_shard_id)
        
        rows = await index_conn.fetch("""
            SELECT primary_key, data_shard_id
            FROM {index_name}_index
            WHERE indexed_value = %s
        """.format(index_name=self.index_name), (indexed_value,))
        
# Step 2: Group by data shard
        by_shard = defaultdict(list)
        for row in rows:
            by_shard[row['data_shard_id']].append(row['primary_key'])
        
# Step 3: Fetch from data shards in parallel
        tasks = []
        for shard_id, keys in by_shard.items():
            task = self._fetch_from_data_shard(shard_id, keys)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
# Flatten results
        return [item for sublist in results for item in sublist]
```

---

## Level 4: Expert

### Production Case Study: Discord's Sharding Architecture

!!! success "Discord's Scale Achievement"
    **Messages**: 1 Trillion+ stored  
    **Throughput**: 4M+ messages/minute peak  
    **Shards**: 4,096 logical shards on 177 Cassandra nodes  
    **Strategy**: Channel-based sharding with time buckets

#### The Problem Discord Solved

| Challenge | Impact | Solution |
|-----------|--------|----------|
| **Hot Channels** | Popular servers crushing single shards | Dynamic bucket redistribution |
| **Time-Series Data** | Old messages queried rarely | Time-bucketed tables |
| **Global Search** | Can't search across all shards | Elasticsearch secondary index |
| **Live Updates** | Millions of concurrent connections | Gateway sharding separate from data |

#### Discord's Sharding Implementation

```python
class DiscordShardingArchitecture:
    """
    Actual patterns from Discord's infrastructure:
    - Channel ID determines shard (messages from same channel together)
    - Message ID contains timestamp (Snowflake IDs)
    - Bucket abstraction allows resharding without app changes
    """
    
    def __init__(self):
        self.bucket_count = 4096  # Number of buckets
        self.buckets_per_shard = 32  # Buckets grouped into shards
        self.shard_count = self.bucket_count // self.buckets_per_shard
        self.hash_ring = ConsistentHashRing(self.bucket_count)
        self.shard_map = {}
        self.shard_metrics = defaultdict(lambda: {
            'qps': 0,
            'size_mb': 0,
            'latency_p99': 0
        })
    
    def get_message_location(self, channel_id: str, message_id: str) -> Dict:
        """
        Determine where to store/retrieve a message
        Discord uses Channel ID for bucket, Message ID (Snowflake) for time ordering
        """
        bucket_id = self.hash_ring.get_bucket(channel_id)
        shard_id = self.get_shard_for_bucket(bucket_id)
        timestamp = self.extract_timestamp(message_id)
        time_bucket = self.get_time_bucket(timestamp)
        
        return {
            'bucket_id': bucket_id,
            'shard_id': shard_id,
            'table': f"messages_{time_bucket}",
            'partition_key': channel_id,
            'clustering_key': message_id
        }
    
    def handle_hot_shard(self, shard_id: int):
        """Handle hot shards by splitting buckets"""
        metrics = self.shard_metrics[shard_id]
        
        if (metrics['qps'] > 10000 or 
            metrics['size_mb'] > 100000 or
            metrics['latency_p99'] > 100):
            
            hot_buckets = self.identify_hot_buckets(shard_id)
            migration_plan = self.create_migration_plan(hot_buckets)
            self.execute_bucket_migration(migration_plan)
    
    def create_migration_plan(self, hot_buckets: List[int]) -> Dict:
        """Create plan to redistribute hot buckets"""
        plan = {'migrations': [], 'new_shards': []}
        available_shards = self.find_shards_with_capacity()
        
        if len(available_shards) < len(hot_buckets):
            new_shard_count = len(hot_buckets) - len(available_shards)
            plan['new_shards'] = self.provision_new_shards(new_shard_count)
            available_shards.extend(plan['new_shards'])
        
        for i, bucket_id in enumerate(hot_buckets):
            target_shard = available_shards[i % len(available_shards)]
            plan['migrations'].append({
                'bucket_id': bucket_id,
                'source_shard': self.get_shard_for_bucket(bucket_id),
                'target_shard': target_shard,
                'estimated_size': self.estimate_bucket_size(bucket_id)
            })
        
        return plan
    
    async def query_channel_messages(
        self, 
        channel_id: str,
        before_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Query messages for a channel with pagination"""
        location = self.get_message_location(channel_id, before_id or "0")
        
        query = """
            SELECT message_id, author_id, content, timestamp
            FROM {table}
            WHERE channel_id = %s
        """.format(table=location['table'])
        
        params = [channel_id]
        
        if before_id:
            query += " AND message_id < %s"
            params.append(before_id)
        
        query += " ORDER BY message_id DESC LIMIT %s"
        params.append(limit)
        
        shard_conn = self.get_shard_connection(location['shard_id'])
        results = await shard_conn.fetch(query, *params)
        
        return [dict(row) for row in results]
```

### Production Case Study: YouTube's Vitess

!!! success "YouTube's Scale with Vitess"
    **Videos**: 500 hours uploaded/minute  
    **Views**: 1 billion hours watched/day  
    **Shards**: 100,000+ MySQL instances  
    **Strategy**: Vitess proxy handles routing, resharding, and failover

#### Why YouTube Built Vitess

| MySQL Limitation | Vitess Solution | Benefit |
|------------------|-----------------|----------|
| **Single Master** | Horizontal sharding | Unlimited write scaling |
| **Manual Sharding** | Automatic routing | Application transparency |
| **Complex Resharding** | Online resharding | Zero downtime scaling |
| **No Connection Pooling** | Built-in pooling | Handle millions of connections |

#### Vitess Architecture in Action

```python
class VitessShardingManager:
    """
    Key Vitess concepts demonstrated:
    - VTGate: Stateless proxy that routes queries
    - VTTablet: Manages a single shard
    - Vindexes: Pluggable sharding schemes
    """
    
    def __init__(self):
        self.keyspace_schema = {}
        self.vindex_map = {}  # Vitess index for routing
        self.shard_topology = {}
        
    def define_sharding_scheme(self, table: str, config: Dict):
        """
        Define how a table should be sharded
        
        Vitess concepts:
        - Keyspace: Logical database
        - Shard: Physical partition
        - Vindex: Index for shard routing
        """
        
        self.keyspace_schema[table] = {
            'sharding_column': config['sharding_column'],
            'vindex_type': config['vindex_type'],
            'shard_count': config['shard_count']
        }
        
# Create vindex based on type
        if config['vindex_type'] == 'hash':
            self.vindex_map[table] = HashVindex(config['shard_count'])
        elif config['vindex_type'] == 'range':
            self.vindex_map[table] = RangeVindex(config['ranges'])
        elif config['vindex_type'] == 'lookup':
            self.vindex_map[table] = LookupVindex(config['lookup_table'])
    
    def route_query(self, query: str) -> List[Dict]:
        """
        Route query to appropriate shards
        
        Vitess query routing:
        1. Parse query to extract table and conditions
        2. Use vindex to determine target shards
        3. Execute on shards in parallel
        4. Merge results
        """
        
# Parse query
        parsed = self.parse_query(query)
        table = parsed['table']
        conditions = parsed['conditions']
        
# Determine target shards
        target_shards = self.get_target_shards(table, conditions)
        
# Scatter query to shards
        shard_queries = []
        for shard_id in target_shards:
            shard_query = self.rewrite_query_for_shard(query, shard_id)
            shard_queries.append((shard_id, shard_query))
        
# Execute in parallel
        results = self.execute_scatter_gather(shard_queries)
        
# Merge results based on query type
        if parsed['query_type'] == 'SELECT':
            return self.merge_select_results(results, parsed)
        elif parsed['query_type'] == 'AGGREGATE':
            return self.merge_aggregate_results(results, parsed)
    
    def handle_cross_shard_transaction(self, operations: List[Dict]):
        """
        Handle transactions spanning multiple shards
        
        Vitess uses 2PC (Two-Phase Commit):
        1. Prepare phase on all shards
        2. Commit phase if all prepared
        3. Rollback if any failed
        """
        
# Group operations by shard
        ops_by_shard = defaultdict(list)
        for op in operations:
            shard_id = self.get_shard_for_operation(op)
            ops_by_shard[shard_id].append(op)
        
# Start distributed transaction
        dtx_id = self.generate_dtx_id()
        
# Phase 1: Prepare
        prepare_results = {}
        for shard_id, shard_ops in ops_by_shard.items():
            try:
                prepared = self.prepare_on_shard(
                    shard_id, 
                    dtx_id, 
                    shard_ops
                )
                prepare_results[shard_id] = prepared
            except Exception as e:
# Prepare failed, abort
                self.abort_transaction(dtx_id, prepare_results)
                raise
        
# Phase 2: Commit
        for shard_id in prepare_results:
            self.commit_on_shard(shard_id, dtx_id)
        
        return {'transaction_id': dtx_id, 'status': 'committed'}
```

### Economic Impact Analysis

```python
class ShardingEconomicsAnalyzer:
    """Analyze economic impact of sharding strategies"""
    
    def analyze_sharding_roi(
        self,
        current_state: Dict,
        sharding_proposal: Dict
    ) -> Dict:
        """Calculate ROI of implementing sharding"""
        
# Current costs (single large database)
        current_costs = {
            'hardware': self._calculate_vertical_scaling_cost(
                current_state['data_size_tb'],
                current_state['qps']
            ),
            'licenses': current_state['db_licenses_annual'],
            'operations': current_state['dba_hours_weekly'] * 52 * 150,
            'downtime': current_state['downtime_hours_annual'] * 
                       current_state['revenue_per_hour']
        }
        
# Projected costs with sharding
        shard_count = sharding_proposal['shard_count']
        sharded_costs = {
            'hardware': self._calculate_horizontal_scaling_cost(
                current_state['data_size_tb'],
                current_state['qps'],
                shard_count
            ),
            'licenses': sharding_proposal['db_licenses_annual'],
            'operations': sharding_proposal['dba_hours_weekly'] * 52 * 150,
            'development': sharding_proposal['development_hours'] * 150,
            'migration': sharding_proposal['migration_hours'] * 150
        }
        
# Benefits
        benefits = {
            'improved_performance': self._calculate_performance_value(
                current_state['avg_latency_ms'],
                sharding_proposal['expected_latency_ms']
            ),
            'increased_capacity': self._calculate_capacity_value(
                current_state['max_qps'],
                sharding_proposal['max_qps']
            ),
            'reduced_downtime': (
                current_state['downtime_hours_annual'] - 
                sharding_proposal['expected_downtime_hours']
            ) * current_state['revenue_per_hour']
        }
        
# Calculate ROI
        annual_savings = (
            sum(current_costs.values()) - 
            sum(sharded_costs.values()) + 
            sum(benefits.values())
        )
        
        implementation_cost = (
            sharded_costs['development'] + 
            sharded_costs['migration']
        )
        
        return {
            'implementation_cost': implementation_cost,
            'annual_savings': annual_savings,
            'payback_months': implementation_cost / (annual_savings / 12),
            'five_year_roi': (annual_savings * 5 - implementation_cost) / 
                           implementation_cost * 100
        }
```

---

## Level 5: Mastery

### Theoretical Foundations

#### Optimal Shard Count Determination
```python
import numpy as np
from scipy.optimize import minimize_scalar

class OptimalShardingCalculator:
    """
    Calculate optimal shard count using queuing theory
    and cost optimization
    """
    
    def calculate_optimal_shards(
        self,
        total_data_size: float,  # TB
        query_rate: float,       # QPS
        growth_rate: float,      # Annual %
        constraints: Dict
    ) -> Dict:
        """
        Find optimal shard count balancing:
        - Query performance
        - Cost efficiency
        - Operational complexity
        """
        
        def cost_function(shard_count):
# Hardware cost (decreases with more shards due to smaller instances)
            hw_cost = self._hardware_cost(
                total_data_size / shard_count,
                query_rate / shard_count
            ) * shard_count
            
# Operational cost (increases with more shards)
            ops_cost = self._operational_cost(shard_count)
            
# Performance penalty (decreases with more shards)
            perf_penalty = self._performance_penalty(
                query_rate / shard_count,
                constraints['max_latency_ms']
            )
            
# Cross-shard query penalty (increases with more shards)
            cross_shard_penalty = self._cross_shard_penalty(
                shard_count,
                constraints['cross_shard_query_ratio']
            )
            
            return hw_cost + ops_cost + perf_penalty + cross_shard_penalty
        
# Find optimal shard count
        result = minimize_scalar(
            cost_function,
            bounds=(1, 100),
            method='bounded'
        )
        
        optimal_shards = int(result.x)
        
# Calculate characteristics at optimal point
        shard_size = total_data_size / optimal_shards
        shard_qps = query_rate / optimal_shards
        
# Project growth
        years_until_reshard = self._calculate_reshard_timeline(
            shard_size,
            shard_qps,
            growth_rate,
            constraints
        )
        
        return {
            'optimal_shard_count': optimal_shards,
            'shard_size_tb': shard_size,
            'shard_qps': shard_qps,
            'annual_cost': cost_function(optimal_shards),
            'years_until_reshard': years_until_reshard,
            'recommendations': self._generate_recommendations(
                optimal_shards,
                shard_size,
                shard_qps
            )
        }
    
    def _hardware_cost(self, size_tb: float, qps: float) -> float:
        """Estimate hardware cost for given size and QPS"""
# Based on cloud provider pricing
# Larger instances have worse $/GB ratio
        storage_cost = size_tb * 100 * (1 + 0.1 * np.log(size_tb))
        compute_cost = qps * 0.01 * (1 + 0.05 * np.log(qps))
        return storage_cost + compute_cost
    
    def _cross_shard_penalty(
        self, 
        shard_count: int, 
        cross_shard_ratio: float
    ) -> float:
        """Calculate penalty for cross-shard operations"""
# More shards = more cross-shard queries
# Penalty grows super-linearly
        return cross_shard_ratio * (shard_count ** 1.5) * 1000
```

### Advanced Sharding Algorithms

```python
class AdvancedShardingAlgorithms:
    """State-of-the-art sharding algorithms"""
    
    def jump_consistent_hash(self, key: int, num_buckets: int) -> int:
        """
        Google's Jump Consistent Hash
        - No memory overhead
        - Consistent bucket reassignment
        - O(ln n) time complexity
        """
        b = -1
        j = 0
        
        while j < num_buckets:
            b = j
            key = ((key * 2862933555777941757) + 1) & 0xffffffffffffffff
            j = int((b + 1) * (2**31 / ((key >> 33) + 1)))
        
        return b
    
    def maglev_hashing(self, backends: List[str], table_size: int = 65537):
        """
        Google's Maglev consistent hashing
        Used in their load balancers
        - Minimal disruption on changes
        - Even distribution
        - Fast lookup
        """
        
        def hash_1(x):
            return hash(x + "_1") % table_size
        
        def hash_2(x):
            return hash(x + "_2") % table_size
        
        n = len(backends)
        lookup = [-1] * table_size
        
# Build permutation for each backend
        permutations = []
        for backend in backends:
            offset = hash_1(backend)
            skip = hash_2(backend)
            
            permutation = []
            for j in range(table_size):
                permutation.append((offset + j * skip) % table_size)
            
            permutations.append(permutation)
        
# Build lookup table
        next_pos = [0] * n
        for i in range(table_size):
            for j in range(n):
                c = permutations[j][next_pos[j]]
                
                while lookup[c] != -1:
                    next_pos[j] += 1
                    c = permutations[j][next_pos[j]]
                
                lookup[c] = j
                next_pos[j] += 1
                break
        
        return lookup
    
    def bounded_load_consistent_hash(
        self, 
        key: str,
        nodes: List[str],
        load_factor: float = 1.25
    ) -> str:
        """
        Consistent hashing with bounded loads
        Ensures no node gets overloaded
        """
        
# Calculate capacity for each node
        avg_load = 1.0 / len(nodes)
        max_load = avg_load * load_factor
        
        node_loads = {node: 0.0 for node in nodes}
        
# Try nodes in consistent hash order
        for i in range(len(nodes)):
            node = self._consistent_hash_node(key, nodes, i)
            
            if node_loads[node] < max_load:
                node_loads[node] += 1.0 / len(nodes)
                return node
        
# Fallback to least loaded
        return min(node_loads.items(), key=lambda x: x[1])[0]
```

### Future Directions

1. **AI-Driven Sharding**
   - ML models predicting optimal shard placement
   - Automatic hot spot detection and mitigation
   - Predictive resharding before issues occur

2. **Quantum-Resistant Sharding**
   - Post-quantum cryptographic sharding
   - Quantum-safe consensus protocols
   - Entanglement-inspired shard coordination

3. **Edge-Native Sharding**
   - Geo-distributed sharding at edge
   - 5G network-aware shard placement
   - Latency-optimized routing

4. **Blockchain Sharding**
   - State sharding for blockchain scalability
   - Cross-shard atomic swaps
   - Sharded consensus mechanisms

---

## Quick Reference

### Sharding Strategy Selection

| If you have... | Use this strategy | Key considerations |
|----------------|-------------------|-------------------|
| Numeric IDs | Range sharding | Watch for hotspots |
| Random keys | Hash sharding | No range queries |
| Geographic data | Location sharding | Data sovereignty |
| Time-series | Time-based sharding | Easy archival |
| Multi-tenant | Tenant sharding | Isolation guaranteed |
| Complex queries | Directory sharding | Additional hop |


### Implementation Checklist

- [ ] Choose sharding key wisely (can't change easily)
- [ ] Plan for resharding from day one
- [ ] Implement shard-aware connection pooling
- [ ] Build cross-shard query capabilities
- [ ] Add shard monitoring and metrics
- [ ] Create shard management tools
- [ ] Test shard failure scenarios
- [ ] Document shard topology
- [ ] Plan backup strategy per shard
- [ ] Consider compliance requirements

### Common Anti-Patterns & How to Avoid Them

| Anti-Pattern | Why It Happens | How to Avoid | Real Example |
|--------------|----------------|--------------|---------------|
| **Sharding Too Early** | FOMO, overengineering | Wait for actual pain | Startup with 1K users sharded, spent 6 months fixing bugs |
| **Wrong Shard Key** | Didn't analyze access patterns | 1 month of query analysis first | Company sharded by user_id, but queries were by company_id |
| **No Resharding Plan** | "We'll figure it out later" | Design resharding on day 1 | Pinterest spent 1 year resharding after explosive growth |
| **UUID Shard Keys** | "It's random, so balanced!" | Can't do range queries | Had to maintain secondary indexes for everything |
| **Cross-Shard JOINs** | Didn't denormalize enough | Denormalize or use different pattern | 30-second queries, rewrote entire data model |

---

## When to Use Sharding: Decision Framework

### Signs You Need Sharding NOW

!!! danger "Red Flags - Immediate Action Required"
    | Symptom | Threshold | Impact if Ignored |
    |---------|-----------|-------------------|
    | **Write Latency** | >500ms P99 | User experience degradation |
    | **Storage** | >5TB or 80% full | Outage risk within weeks |
    | **CPU** | >80% sustained | Cascading failures likely |
    | **Connections** | >80% of max | Connection pool exhaustion |
    | **Replication Lag** | >10 seconds | Data inconsistency issues |

### Sharding Readiness Checklist

| Requirement | Why It Matters | Without It |
|-------------|----------------|------------|
| **Unique shard key identified** | Determines data distribution | Hotspots, failed sharding |
| **No cross-shard JOINs** | JOINs become distributed queries | 100x performance hit |
| **Application can handle eventual consistency** | Shards may have lag | Data corruption risk |
| **DevOps team trained** | Complexity increases 10x | Operational disasters |
| **Monitoring in place** | Must track per-shard metrics | Blind to problems |
| **Resharding strategy defined** | Will need it within 2 years | Massive migration project |

### Cost-Benefit Analysis

#### When Sharding Pays Off

```python
# Simple ROI calculation
def should_we_shard(current_metrics):
    # Costs
    implementation_cost = 200_000  # Engineering time
    operational_overhead = 50_000  # Annual extra complexity
    
    # Current pain
    downtime_cost_per_hour = 100_000
    current_downtime_hours_yearly = 50
    current_cost = downtime_cost_per_hour * current_downtime_hours_yearly
    
    # After sharding
    expected_downtime_reduction = 0.9  # 90% less downtime
    savings = current_cost * expected_downtime_reduction
    
    roi_months = implementation_cost / (savings / 12)
    
    return {
        'implement': roi_months < 12,
        'roi_months': roi_months,
        'yearly_savings': savings - operational_overhead
    }
```

### Alternative Solutions to Try First

| Problem | Try This First | Before Sharding |
|---------|----------------|------------------|
| **Slow queries** | Query optimization, indexes | 10x easier than sharding |
| **High CPU** | Vertical scaling, caching | Can buy 6-12 months |
| **Storage full** | Archival, compression | Reduces data by 50-90% |
| **Write bottleneck** | Write-through cache, queuing | Handles burst traffic |
| **Read scaling** | Read replicas, caching | Scales to 10x reads |

---

## 🎓 Key Takeaways

1. **Shard key selection is critical** - It determines everything
2. **Plan for resharding** - Data grows, patterns change
3. **Monitor shard health** - Detect hotspots early
4. **Minimize cross-shard operations** - They're expensive
5. **Automate shard management** - Manual doesn't scale

---

*"The best sharding strategy is the one that lets you sleep at night while your data doubles."*

---

## Related Topics

### Foundational Concepts
- [Consistent Hashing](case-studies/consistent-hashing) - Core algorithm for data distribution
- [CAP Theorem](quantitative/cap-theorem) - Understanding trade-offs in distributed data
- [Partitioning Strategies](patterns/partitioning) - Different ways to split data

### Related Patterns
- [Database Federation](patterns/federation) - Alternative scaling approach
- [CQRS](patterns/cqrs) - Separate read/write paths (works well with sharding)
- [Event Sourcing](patterns/event-sourcing) - Append-only sharding strategy
- [Cache Sharding](patterns/cache-sharding) - Distributed caching patterns

### Implementation Patterns
- [Service Mesh](patterns/service-mesh) - Managing shard routing at network level
- [Saga Pattern](patterns/saga) - Distributed transactions across shards
- [API Gateway](patterns/api-gateway) - Hide sharding complexity from clients

### Case Studies
- [Discord Message Sharding](case-studies/chat-system) - 1T+ messages
- [Uber's Schemaless](case-studies/uber-schemaless/) - Dynamic sharding
- [Instagram's Cassandra](case-studies/instagram-cassandra/) - User feed sharding
- [Pinterest Sharding Journey](case-studies/pinterest-sharding/) - Resharding at scale

### Operational Excellence
- [Monitoring Distributed Systems](human-factors/monitoring/) - Per-shard observability
- [Chaos Engineering](human-factors/chaos-engineering.md) - Testing shard failures
- [Capacity Planning](human-factors/capacity-planning/) - When to add shards

---

<div class="page-nav" markdown>
[:material-arrow-left: CDC](patterns/cdc) | 
[:material-arrow-up: Patterns](patterns) | 
[:material-arrow-right: Caching Strategies](patterns/caching-strategies)
</div>