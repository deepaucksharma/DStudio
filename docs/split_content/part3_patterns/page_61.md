Page 61: Geo-Replication Playbooks
Data follows users around the globe
THE PROBLEM
Global users, single region:
- High latency for distant users
- Disaster recovery risk
- Compliance issues (data residency)
- Single region capacity limits
THE SOLUTION
Multiple deployment patterns:

1. Active-Passive: Primary + DR standby
2. Active-Active: All regions accept writes
3. Follow-the-Sun: Primary migrates
4. Geo-Partitioned: Regional data ownership
PSEUDO CODE IMPLEMENTATION
GeoReplicationManager:
    topology = load_topology_config()
    
    write(key, value, options):
        primary_region = determine_primary(key)
        
        // Write to primary
        primary_result = regions[primary_region].write(key, value)
        
        // Replicate based on strategy
        if options.sync_replication:
            sync_replicate_to_regions(key, value)
        else:
            async_replicate_to_regions(key, value)
            
        return primary_result
        
    read(key, options):
        if options.strong_consistency:
            region = determine_primary(key)
            return regions[region].read(key)
        else:
            // Read from nearest
            nearest = find_nearest_region()
            return regions[nearest].read(key)

ConflictResolution:
    resolve_concurrent_writes(versions):
        strategy = config.conflict_resolution
        
        if strategy == 'LAST_WRITE_WINS':
            return max(versions, key=lambda v: v.timestamp)
            
        elif strategy == 'VECTOR_CLOCK':
            return vector_clock_merge(versions)
            
        elif strategy == 'CUSTOM':
            return business_logic_merge(versions)
            
        elif strategy == 'ALL_VERSIONS':
            return versions  // Let app decide

ActiveActiveReplication:
    handle_write(region, key, value):
        // Local write
        local_version = write_locally(key, value)
        
        // Broadcast to other regions
        for remote_region in other_regions:
            send_async(remote_region, {
                'key': key,
                'value': value,
                'version': local_version,
                'origin': region
            })
            
    handle_remote_write(message):
        // Check for conflicts
        local_version = get_version(message.key)
        
        if has_conflict(local_version, message.version):
            resolved = resolve_conflict(local_version, message)
            write_locally(message.key, resolved)
        else:
            write_locally(message.key, message.value)

CrossRegionConsistency:
    ensure_read_your_writes(session):
        // Track write timestamp per session
        last_write_time = session.last_write_timestamp
        
        // Ensure replica has caught up
        wait_for_replication(last_write_time)
        
        return read_from_local_replica()
Geo-Replication Strategies:
1. MASTER-SLAVE REPLICATION
   US-East (Master) → US-West (Slave)
                   → EU (Slave)
                   → Asia (Slave)

2. MULTI-MASTER RING
   US ←→ EU ←→ Asia ←→ US

3. HIERARCHICAL REPLICATION
   Global Master → Regional Masters → Local Replicas

4. CONFLICT-FREE REPLICATED
   Each region has CRDTs
   Automatic merge on sync
✓ CHOOSE THIS WHEN:

Global user base
Disaster recovery required
Data residency laws
Read latency critical
Regional failure tolerance

⚠️ BEWARE OF:

Replication lag
Conflict resolution complexity
Network partition handling
Compliance boundaries
Operational complexity

REAL EXAMPLES

Google Spanner: Global consistency
DynamoDB Global: Multi-region tables
CockroachDB: Geo-partitioning
