# Episode 026: Database Sharding - Part 2: Implementation Patterns and Challenges
## Mumbai-Style Tech Podcast - Hindi/English Mix

---

**Episode Duration**: 60 minutes (Part 2 of 3)  
**Target Audience**: Software Engineers, Database Engineers, System Architects  
**Language**: 70% Hindi/Roman Hindi, 30% Technical English  
**Style**: Mumbai Street-level Storytelling  

---

## [Opening Theme Music - Mumbai Traffic Sound]

**Host**: Welcome back doston! Part 1 mein humne dekha ki sharding kya hai, ab Part 2 mein real implementation ki challenges dekh lete hain. Ye bilkul Mumbai mein flat hunt karne jaisa hai - paper mein sab perfect lagta hai, reality mein jaake pata chalta hai ki kitni complications hain!

Aaj ka focus hai:
- Cross-shard transactions की complexity
- Data migration aur resharding strategies  
- Monitoring aur troubleshooting techniques
- Real production challenges aur solutions
- Code examples Java, Go, Python mein

Toh chalo shuru karte hain implementation ki duniya mein!

---

## Section 1: Cross-Shard Transactions - Inter-Zone Train Travel Jaisa

**Host**: Doston, cross-shard transaction bilkul waise hai jaise Mumbai mein ek zone se doosre zone mein jaana. Suppose tumhe Andheri se Thane jana hai - Western Railway se Central Railway. Simple nahi hai, interchange chahiye, timing match karni padegi, aur agar koi train delay hui toh poora plan bigad jata hai.

### The Complexity of Distributed Transactions

```python
class CrossShardTransactionManager:
    """
    Cross-shard transactions का management
    Multiple shards में atomic operations ensure करना
    """
    def __init__(self, shard_connections):
        self.shards = shard_connections
        self.active_transactions = {}
        self.transaction_timeout = 30  # 30 seconds timeout
        
    def begin_distributed_transaction(self, transaction_id, involved_shards):
        """
        Distributed transaction शुरू करना - सभी involved shards के साथ
        """
        transaction_context = {
            "transaction_id": transaction_id,
            "involved_shards": involved_shards,
            "status": "PREPARING",
            "prepared_shards": set(),
            "start_time": time.time(),
            "operations": []
        }
        
        self.active_transactions[transaction_id] = transaction_context
        
        # Phase 1: Send PREPARE to all shards
        prepare_results = {}
        for shard_id in involved_shards:
            try:
                result = self.send_prepare_to_shard(shard_id, transaction_id)
                prepare_results[shard_id] = result
                
                if result["status"] == "PREPARED":
                    transaction_context["prepared_shards"].add(shard_id)
                    
            except Exception as e:
                prepare_results[shard_id] = {"status": "FAILED", "error": str(e)}
        
        return self.decide_commit_or_abort(transaction_id, prepare_results)
    
    def send_prepare_to_shard(self, shard_id, transaction_id):
        """
        Individual shard को PREPARE message भेजना
        """
        shard = self.shards.get(shard_id)
        if not shard:
            return {"status": "FAILED", "error": "Shard not found"}
        
        try:
            # Simulate preparing transaction on shard
            # Real implementation would:
            # 1. Lock required records
            # 2. Validate all constraints  
            # 3. Write to transaction log
            # 4. Reserve resources
            
            preparation_time = random.uniform(0.1, 0.5)  # Simulate network + processing time
            time.sleep(preparation_time)
            
            # Simulate 95% success rate for preparation
            if random.random() < 0.95:
                return {
                    "status": "PREPARED",
                    "shard_id": shard_id,
                    "timestamp": time.time(),
                    "resources_locked": True
                }
            else:
                return {
                    "status": "FAILED", 
                    "error": "Resource conflict or constraint violation"
                }
                
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def decide_commit_or_abort(self, transaction_id, prepare_results):
        """
        सभी shards के PREPARE results के basis पर commit/abort decision
        """
        transaction_context = self.active_transactions[transaction_id]
        all_shards = set(transaction_context["involved_shards"])
        prepared_shards = transaction_context["prepared_shards"]
        
        # Check if all shards prepared successfully
        if prepared_shards == all_shards:
            # All shards prepared - proceed with COMMIT
            return self.commit_transaction(transaction_id)
        else:
            # Some shards failed - ABORT transaction  
            return self.abort_transaction(transaction_id, prepare_results)
    
    def commit_transaction(self, transaction_id):
        """
        Transaction को commit करना - सभी shards पर COMMIT भेजना
        """
        transaction_context = self.active_transactions[transaction_id]
        transaction_context["status"] = "COMMITTING"
        
        commit_results = {}
        
        for shard_id in transaction_context["involved_shards"]:
            try:
                # Send COMMIT to each prepared shard
                result = self.send_commit_to_shard(shard_id, transaction_id)
                commit_results[shard_id] = result
                
            except Exception as e:
                # Commit failure is serious - log for manual intervention
                commit_results[shard_id] = {"status": "COMMIT_FAILED", "error": str(e)}
                self.log_commit_failure(transaction_id, shard_id, str(e))
        
        transaction_context["status"] = "COMMITTED"
        transaction_context["end_time"] = time.time()
        
        return {
            "transaction_id": transaction_id,
            "final_status": "COMMITTED",
            "duration": transaction_context["end_time"] - transaction_context["start_time"],
            "commit_results": commit_results
        }
    
    def abort_transaction(self, transaction_id, prepare_results):
        """
        Transaction को abort करना - सभी prepared shards को ABORT भेजना
        """
        transaction_context = self.active_transactions[transaction_id]
        transaction_context["status"] = "ABORTING"
        
        # Send ABORT to all shards that were prepared
        for shard_id in transaction_context["prepared_shards"]:
            try:
                self.send_abort_to_shard(shard_id, transaction_id)
            except Exception as e:
                # Log abort failures for monitoring
                self.log_abort_failure(transaction_id, shard_id, str(e))
        
        transaction_context["status"] = "ABORTED"
        transaction_context["end_time"] = time.time()
        
        return {
            "transaction_id": transaction_id,
            "final_status": "ABORTED",
            "duration": transaction_context["end_time"] - transaction_context["start_time"],
            "prepare_results": prepare_results
        }

# Cross-shard transaction example - Inter-bank money transfer
def demonstrate_cross_shard_transaction():
    """
    Real-world example: Money transfer between different banks
    """
    # Setup shards for different banks
    shard_connections = {
        "SBI_SHARD": {"host": "sbi-db.bank.in", "status": "active"},
        "HDFC_SHARD": {"host": "hdfc-db.bank.in", "status": "active"}, 
        "ICICI_SHARD": {"host": "icici-db.bank.in", "status": "active"}
    }
    
    tx_manager = CrossShardTransactionManager(shard_connections)
    
    # Money transfer from SBI account to HDFC account  
    transfer_transaction = {
        "from_account": "SBI_123456789",
        "to_account": "HDFC_987654321", 
        "amount": 50000,  # ₹50,000
        "transaction_type": "NEFT"
    }
    
    involved_shards = ["SBI_SHARD", "HDFC_SHARD"]  # Two banks involved
    transaction_id = f"TXN_{int(time.time())}"
    
    print(f"🏦 Inter-Bank Money Transfer Transaction")
    print(f"Transaction ID: {transaction_id}")
    print(f"From: {transfer_transaction['from_account']}")
    print(f"To: {transfer_transaction['to_account']}")
    print(f"Amount: ₹{transfer_transaction['amount']:,}")
    print(f"Involved Shards: {involved_shards}")
    
    # Execute distributed transaction
    result = tx_manager.begin_distributed_transaction(transaction_id, involved_shards)
    
    print(f"\nTransaction Result:")
    print(f"Status: {result['final_status']}")
    print(f"Duration: {result['duration']:.2f} seconds")
    
    if result['final_status'] == 'COMMITTED':
        print("✅ Money transfer successful!")
    else:
        print("❌ Money transfer failed - amount will be refunded")
        
    return result

# Run the demonstration
demonstrate_cross_shard_transaction()
```

### Real Challenge: Network Partitions and Failures

Mumbai local trains mein bhi same problem hoti hai - agar Central Railway down ho gaya, toh Western Railway se CST jaane ka koi direct way nahi hai. Database sharding mein ye **network partition** problem kehte hain.

```java
// Java implementation for handling network partitions
public class ResilientShardManager {
    private final Map<String, ShardConnection> primaryShards;
    private final Map<String, ShardConnection> replicaShards;
    private final CircuitBreakerManager circuitBreaker;
    
    public class ShardConnection {
        private String host;
        private int port;
        private ConnectionState state;
        private long lastHealthCheck;
        
        public boolean isHealthy() {
            // Health check logic
            long currentTime = System.currentTimeMillis();
            if (currentTime - lastHealthCheck > 30000) { // 30 seconds
                return performHealthCheck();
            }
            return state == ConnectionState.HEALTHY;
        }
        
        private boolean performHealthCheck() {
            try {
                // Mumbai-style ping: "Arre bhai, sab theek hai na?"
                Connection conn = DriverManager.getConnection(
                    "jdbc:postgresql://" + host + ":" + port + "/sharddb"
                );
                
                PreparedStatement stmt = conn.prepareStatement("SELECT 1");
                ResultSet rs = stmt.executeQuery();
                
                boolean healthy = rs.next() && rs.getInt(1) == 1;
                this.state = healthy ? ConnectionState.HEALTHY : ConnectionState.UNHEALTHY;
                this.lastHealthCheck = System.currentTimeMillis();
                
                return healthy;
                
            } catch (SQLException e) {
                this.state = ConnectionState.UNHEALTHY;
                this.lastHealthCheck = System.currentTimeMillis();
                return false;
            }
        }
    }
    
    public CompletableFuture<QueryResult> executeWithFallback(
            String shardKey, 
            String query, 
            Object... params) {
        
        String primaryShardId = determineShardId(shardKey);
        ShardConnection primaryShard = primaryShards.get(primaryShardId);
        
        return CompletableFuture.supplyAsync(() -> {
            // Try primary shard first
            if (primaryShard.isHealthy()) {
                try {
                    return executeFastQuery(primaryShard, query, params);
                } catch (DatabaseException e) {
                    // Primary shard failed during execution
                    circuitBreaker.recordFailure(primaryShardId);
                }
            }
            
            // Fallback to replica shard
            ShardConnection replicaShard = replicaShards.get(primaryShardId);
            if (replicaShard != null && replicaShard.isHealthy()) {
                try {
                    return executeSlowQuery(replicaShard, query, params);
                } catch (DatabaseException e) {
                    circuitBreaker.recordFailure(primaryShardId + "_replica");
                }
            }
            
            // Both primary and replica failed - return degraded response
            return createDegradedResponse("Shard temporarily unavailable");
        });
    }
    
    private QueryResult executeFastQuery(ShardConnection shard, String query, Object... params) {
        // Fast path execution with lower timeout
        // Mumbai local ki tarah - direct route, kam time
        return executeQueryWithTimeout(shard, query, 1000, params); // 1 second timeout
    }
    
    private QueryResult executeSlowQuery(ShardConnection shard, String query, Object... params) {
        // Slower fallback with higher timeout  
        // Inter-zone travel ki tarah - interchange required, zyada time
        return executeQueryWithTimeout(shard, query, 5000, params); // 5 second timeout
    }
}
```

---

## Section 2: Data Migration and Resharding - Society Redevelopment Jaisa

**Host**: Doston, resharding ka process bilkul Mumbai mein society redevelopment jaisa hai. Purane building ko tod kar nayi building banani hai, but residents ko kahin aur temporary accommodation deni padegi. Sab kuch plan karna padta hai ki koi inconvenience na ho.

### The Resharding Challenge

```python
class ReshardingManager:
    """
    Database resharding का complete management
    Live traffic के saath data को new shards में migrate करना
    """
    def __init__(self, current_shards, target_shards):
        self.current_shards = current_shards
        self.target_shards = target_shards
        self.migration_status = {}
        self.dual_write_mode = False
        
    def plan_resharding_strategy(self, data_distribution_analysis):
        """
        Resharding strategy planning - Society redevelopment plan जैसा
        """
        migration_plan = {
            "total_data_size": data_distribution_analysis["total_size_gb"],
            "estimated_migration_time": self.calculate_migration_time(
                data_distribution_analysis["total_size_gb"]
            ),
            "phases": [],
            "rollback_strategy": {},
            "risk_assessment": {}
        }
        
        # Phase 1: Setup target shards
        migration_plan["phases"].append({
            "phase": 1,
            "name": "Target Shard Setup",
            "duration_hours": 2,
            "activities": [
                "Provision new database servers",
                "Setup replication from current shards", 
                "Create database schemas and indexes",
                "Validate data integrity tools"
            ],
            "success_criteria": "All target shards operational and replicating"
        })
        
        # Phase 2: Dual-write mode
        migration_plan["phases"].append({
            "phase": 2, 
            "name": "Dual Write Mode",
            "duration_hours": 24,  # 1 day of dual writing
            "activities": [
                "Enable dual-write to current and target shards",
                "Monitor write latency impact",
                "Validate data consistency between old and new shards",
                "Fix any consistency issues found"
            ],
            "success_criteria": "Data consistency 99.99%+ between old and new shards"
        })
        
        # Phase 3: Traffic cutover  
        migration_plan["phases"].append({
            "phase": 3,
            "name": "Traffic Cutover",
            "duration_hours": 1,
            "activities": [
                "Switch read traffic to new shards (gradual)",
                "Monitor query performance and error rates",
                "Switch write traffic to new shards", 
                "Disable writes to old shards"
            ],
            "success_criteria": "All traffic on new shards, performance stable"
        })
        
        # Phase 4: Cleanup
        migration_plan["phases"].append({
            "phase": 4,
            "name": "Old Shard Cleanup",
            "duration_hours": 4,
            "activities": [
                "Final data validation",
                "Backup old shards for rollback capability",
                "Decommission old database servers",
                "Update monitoring and alerting"
            ],
            "success_criteria": "Migration completed, old resources cleaned up"
        })
        
        return migration_plan
    
    def execute_dual_write_migration(self, shard_key_range, target_shard_id):
        """
        Dual-write migration execution - दो जगह parallel writing
        """
        print(f"🔄 Starting dual-write migration for range {shard_key_range}")
        
        # Enable dual write mode for this range
        dual_write_config = {
            "source_shard": self.get_current_shard(shard_key_range[0]),
            "target_shard": target_shard_id,
            "key_range": shard_key_range,
            "consistency_check_interval": 300,  # 5 minutes
            "rollback_threshold": 0.01  # 1% error rate triggers rollback
        }
        
        # Start dual writing
        migration_stats = {
            "start_time": time.time(),
            "records_migrated": 0,
            "consistency_errors": 0,
            "performance_impact": {}
        }
        
        try:
            # Simulate migration process
            for i in range(100):  # Simulate 100 batches
                batch_result = self.migrate_data_batch(
                    dual_write_config, batch_size=1000
                )
                
                migration_stats["records_migrated"] += batch_result["records"]
                migration_stats["consistency_errors"] += batch_result["errors"]
                
                # Check if error rate is too high
                error_rate = migration_stats["consistency_errors"] / max(1, migration_stats["records_migrated"])
                if error_rate > dual_write_config["rollback_threshold"]:
                    raise MigrationException(f"Error rate too high: {error_rate:.2%}")
                
                # Simulate progress
                time.sleep(0.01)  # Small delay for demo
                
                if i % 20 == 0:  # Progress update every 20 batches
                    print(f"  Progress: {i}% - {migration_stats['records_migrated']:,} records migrated")
        
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return self.rollback_migration(dual_write_config, migration_stats)
        
        migration_stats["end_time"] = time.time()
        migration_stats["duration"] = migration_stats["end_time"] - migration_stats["start_time"]
        
        print(f"✅ Migration completed successfully!")
        print(f"   Records migrated: {migration_stats['records_migrated']:,}")
        print(f"   Duration: {migration_stats['duration']:.2f} seconds")
        print(f"   Error rate: {migration_stats['consistency_errors']/migration_stats['records_migrated']:.4%}")
        
        return migration_stats
    
    def migrate_data_batch(self, config, batch_size):
        """
        Single batch का data migration
        """
        # Simulate reading from source shard
        source_data = self.read_from_shard(
            config["source_shard"], 
            config["key_range"], 
            batch_size
        )
        
        # Write to target shard
        write_result = self.write_to_shard(
            config["target_shard"],
            source_data
        )
        
        # Verify consistency
        consistency_result = self.verify_batch_consistency(
            config["source_shard"],
            config["target_shard"], 
            source_data
        )
        
        return {
            "records": len(source_data),
            "errors": consistency_result["errors"],
            "write_time": write_result["duration"]
        }
    
    def calculate_migration_time(self, data_size_gb):
        """
        Migration time estimation based on data size
        """
        # Based on real-world experience:
        # - Network bandwidth: 1 Gbps = 125 MB/s = 0.125 GB/s
        # - Database processing overhead: 50% 
        # - Consistency checks overhead: 25%
        
        effective_throughput = 0.125 * 0.5 * 0.75  # GB/s with overheads
        estimated_hours = data_size_gb / (effective_throughput * 3600)
        
        # Add buffer for safety
        return estimated_hours * 1.5

# Mumbai society redevelopment as resharding metaphor
class MumbaiSocietyResharding:
    """
    Mumbai society redevelopment को database resharding के रूप में
    """
    def __init__(self):
        self.old_building = {
            "total_flats": 48,  # 48 flats in old building
            "families": 48,
            "built_year": 1975,
            "condition": "DETERIORATING"
        }
        
        self.new_building = {
            "total_flats": 96,  # Double capacity after redevelopment
            "families": 0,      # Initially empty
            "built_year": 2024,
            "condition": "EXCELLENT"
        }
        
        self.temporary_accommodation = []
    
    def plan_society_redevelopment(self):
        """
        Society redevelopment plan - Resharding strategy jaisa
        """
        plan = {
            "phase_1": {
                "name": "Temporary Relocation",
                "duration_months": 2,
                "activities": [
                    "Find temporary accommodation for all families",
                    "Pack and move belongings",
                    "Ensure utilities connection at temp location",
                    "Demolish old building"
                ]
            },
            "phase_2": {
                "name": "New Construction", 
                "duration_months": 18,
                "activities": [
                    "Clear site and prepare foundation",
                    "Construct new building structure",
                    "Install modern amenities and utilities",
                    "Complete interior work and testing"
                ]
            },
            "phase_3": {
                "name": "Family Relocation Back",
                "duration_months": 1,
                "activities": [
                    "Allocate new flats to families",
                    "Move families from temporary to permanent",
                    "Distribute additional flats to new buyers", 
                    "Complete society formation formalities"
                ]
            }
        }
        
        return plan
    
    def simulate_family_migration(self):
        """
        Family migration simulation - Data migration jaisa
        """
        print("🏠 Mumbai Society Redevelopment Simulation")
        print("=" * 50)
        
        # Phase 1: Move to temporary accommodation
        print("\n📦 Phase 1: Moving to Temporary Accommodation")
        for flat_no in range(1, 49):  # 48 families
            temp_location = f"Temp_Building_{(flat_no-1)//12 + 1}"  # 4 temp buildings
            
            self.temporary_accommodation.append({
                "original_flat": flat_no,
                "temp_location": temp_location,
                "family_id": f"Family_{flat_no:03d}"
            })
            
            if flat_no % 12 == 0:  # Progress update
                print(f"  Moved {flat_no} families to temporary accommodation")
        
        # Phase 2: Construction period (simulated)
        print(f"\n🏗️ Phase 2: Construction in progress...")
        print(f"  Old building demolished")
        print(f"  New building construction: 18 months")
        print(f"  New capacity: {self.new_building['total_flats']} flats")
        
        # Phase 3: Move back to new building
        print(f"\n🔄 Phase 3: Moving back to new building")
        for family in self.temporary_accommodation:
            # Original families get preference for lower floor numbers
            new_flat_no = family["original_flat"]
            
            print(f"  {family['family_id']}: Temp {family['temp_location']} → New Flat {new_flat_no}")
            self.new_building["families"] += 1
        
        # Additional capacity for new residents
        additional_flats = self.new_building["total_flats"] - len(self.temporary_accommodation)
        print(f"\n✅ Redevelopment Complete!")
        print(f"  Original families relocated: {len(self.temporary_accommodation)}")
        print(f"  Additional flats available: {additional_flats}")
        print(f"  Total capacity increase: {additional_flats/len(self.temporary_accommodation)*100:.0f}%")

# Demonstrate both concepts
print("Database Resharding Example:")
print("=" * 30)

# Real resharding scenario
resharding_manager = ReshardingManager(current_shards=4, target_shards=8)

# Analyze current data distribution
data_analysis = {
    "total_size_gb": 500,  # 500 GB total data
    "hot_data_gb": 150,    # 150 GB frequently accessed
    "cold_data_gb": 350,   # 350 GB rarely accessed
    "shard_distribution": {
        "shard_1": 140,  # Overloaded
        "shard_2": 130,  # Overloaded  
        "shard_3": 115,  # Balanced
        "shard_4": 115   # Balanced
    }
}

# Create migration plan
migration_plan = resharding_manager.plan_resharding_strategy(data_analysis)

print(f"Migration Plan Summary:")
print(f"Total Data: {migration_plan['total_data_size']} GB")
print(f"Estimated Time: {migration_plan['estimated_migration_time']:.1f} hours")
print(f"Number of Phases: {len(migration_plan['phases'])}")

# Execute a sample migration
sample_migration = resharding_manager.execute_dual_write_migration(
    shard_key_range=(1000000, 2000000),
    target_shard_id="new_shard_5"
)

print(f"\n" + "="*50)

# Society redevelopment example
society_resharding = MumbaiSocietyResharding()
redevelopment_plan = society_resharding.plan_society_redevelopment()
society_resharding.simulate_family_migration()
```

---

## Section 3: Monitoring and Troubleshooting - Traffic Control Room Jaisa

**Host**: Doston, sharded database ko monitor karna bilkul Mumbai traffic control room jaisa hai. Har signal, har junction pe kya ho raha hai - sab kuch real-time track karna padta hai. Ek jagah problem hui toh poore network pe effect hota hai.

### Comprehensive Monitoring Strategy

```go
// Go implementation for high-performance shard monitoring
package main

import (
    "context"
    "fmt"
    "log"
    "sync"
    "time"
)

// ShardMonitor represents comprehensive shard monitoring system
type ShardMonitor struct {
    shards          map[string]*ShardInfo
    alerting        *AlertManager
    metrics         *MetricsCollector
    healthCheckers  map[string]*HealthChecker
    mu              sync.RWMutex
}

type ShardInfo struct {
    ID                string
    Host              string
    Port              int
    Status            string
    LastHealthCheck   time.Time
    QueryLatencyP99   float64
    ConnectionCount   int
    DiskUsagePercent  float64
    CPUUsagePercent   float64
    QueriesPerSecond  float64
    ErrorRate         float64
}

type HealthChecker struct {
    ShardID       string
    CheckInterval time.Duration
    Timeout       time.Duration
    FailureCount  int
    MaxFailures   int
}

type MetricsCollector struct {
    // Real-time metrics collection
    QueryLatencies    map[string][]float64
    ThroughputHistory map[string][]float64
    ErrorRates        map[string][]float64
}

func NewShardMonitor() *ShardMonitor {
    return &ShardMonitor{
        shards:         make(map[string]*ShardInfo),
        alerting:       NewAlertManager(),
        metrics:        NewMetricsCollector(),
        healthCheckers: make(map[string]*HealthChecker),
    }
}

func (sm *ShardMonitor) StartMonitoring() {
    // Mumbai traffic signal ki tarah - har 30 seconds mein check
    ticker := time.NewTicker(30 * time.Second)
    defer ticker.Stop()

    for {
        select {
        case <-ticker.C:
            sm.performHealthChecks()
            sm.collectMetrics()
            sm.analyzePerformanceTrends()
            sm.checkAlertConditions()
        }
    }
}

func (sm *ShardMonitor) performHealthChecks() {
    sm.mu.RLock()
    defer sm.mu.RUnlock()

    var wg sync.WaitGroup
    
    // Parallel health checks - सभी shards को parallel check करना
    for shardID := range sm.shards {
        wg.Add(1)
        go func(id string) {
            defer wg.Done()
            sm.checkShardHealth(id)
        }(shardID)
    }
    
    wg.Wait()
}

func (sm *ShardMonitor) checkShardHealth(shardID string) {
    shard := sm.shards[shardID]
    
    // Perform comprehensive health check
    healthMetrics := sm.performDetailedHealthCheck(shard)
    
    // Update shard information
    sm.mu.Lock()
    shard.LastHealthCheck = time.Now()
    shard.QueryLatencyP99 = healthMetrics.LatencyP99
    shard.ConnectionCount = healthMetrics.ActiveConnections
    shard.DiskUsagePercent = healthMetrics.DiskUsage
    shard.CPUUsagePercent = healthMetrics.CPUUsage
    shard.QueriesPerSecond = healthMetrics.QPS
    shard.ErrorRate = healthMetrics.ErrorRate
    
    // Determine shard status
    if healthMetrics.IsHealthy {
        shard.Status = "HEALTHY"
        sm.healthCheckers[shardID].FailureCount = 0
    } else {
        sm.healthCheckers[shardID].FailureCount++
        if sm.healthCheckers[shardID].FailureCount >= sm.healthCheckers[shardID].MaxFailures {
            shard.Status = "UNHEALTHY"
            sm.triggerShardFailureAlert(shardID, healthMetrics)
        } else {
            shard.Status = "DEGRADED"
        }
    }
    sm.mu.Unlock()
}

type HealthMetrics struct {
    IsHealthy         bool
    LatencyP99        float64
    ActiveConnections int
    DiskUsage         float64
    CPUUsage          float64
    QPS               float64
    ErrorRate         float64
    ResponseTime      float64
}

func (sm *ShardMonitor) performDetailedHealthCheck(shard *ShardInfo) HealthMetrics {
    // Simulate comprehensive health check
    // Real implementation would:
    // 1. Test database connectivity
    // 2. Execute sample queries and measure latency
    // 3. Check system resources (CPU, memory, disk)
    // 4. Validate data integrity
    // 5. Check replication lag
    
    return HealthMetrics{
        IsHealthy:         true, // Simplified for demo
        LatencyP99:        float64(50 + (time.Now().Unix() % 100)), // Simulated latency
        ActiveConnections: 45,
        DiskUsage:         75.5,
        CPUUsage:          65.2,
        QPS:               1250.0,
        ErrorRate:         0.05, // 0.05%
        ResponseTime:      25.0,
    }
}

func (sm *ShardMonitor) analyzePerformanceTrends() {
    // Mumbai traffic pattern analysis jaisa
    // Peak hours, slow periods, unusual spikes detect करना
    
    sm.mu.RLock()
    defer sm.mu.RUnlock()
    
    for shardID, shard := range sm.shards {
        // Analyze query latency trends
        if shard.QueryLatencyP99 > 1000 { // 1 second threshold
            sm.alerting.TriggerAlert(&Alert{
                Type:        "HIGH_LATENCY",
                ShardID:     shardID,
                Message:     fmt.Sprintf("Shard %s latency high: %.2fms", shardID, shard.QueryLatencyP99),
                Severity:    "WARNING",
                Timestamp:   time.Now(),
            })
        }
        
        // Analyze disk usage
        if shard.DiskUsagePercent > 85 {
            sm.alerting.TriggerAlert(&Alert{
                Type:        "HIGH_DISK_USAGE",
                ShardID:     shardID,
                Message:     fmt.Sprintf("Shard %s disk usage: %.1f%%", shardID, shard.DiskUsagePercent),
                Severity:    "CRITICAL",
                Timestamp:   time.Now(),
            })
        }
        
        // Analyze error rates
        if shard.ErrorRate > 1.0 { // 1% error rate
            sm.alerting.TriggerAlert(&Alert{
                Type:        "HIGH_ERROR_RATE",
                ShardID:     shardID,
                Message:     fmt.Sprintf("Shard %s error rate: %.2f%%", shardID, shard.ErrorRate),
                Severity:    "CRITICAL",
                Timestamp:   time.Now(),
            })
        }
    }
}

type Alert struct {
    Type        string
    ShardID     string
    Message     string
    Severity    string
    Timestamp   time.Time
}

type AlertManager struct {
    activeAlerts map[string]*Alert
    alertHistory []*Alert
    mu           sync.RWMutex
}

func NewAlertManager() *AlertManager {
    return &AlertManager{
        activeAlerts: make(map[string]*Alert),
        alertHistory: make([]*Alert, 0),
    }
}

func (am *AlertManager) TriggerAlert(alert *Alert) {
    am.mu.Lock()
    defer am.mu.Unlock()
    
    alertKey := fmt.Sprintf("%s_%s", alert.ShardID, alert.Type)
    am.activeAlerts[alertKey] = alert
    am.alertHistory = append(am.alertHistory, alert)
    
    // Send notifications (simplified)
    fmt.Printf("🚨 ALERT: %s - %s\n", alert.Severity, alert.Message)
    
    // Real implementation would:
    // 1. Send emails to on-call engineers
    // 2. Send SMS for critical alerts
    // 3. Post to Slack/Teams channels
    // 4. Create tickets in monitoring systems
    // 5. Trigger automated remediation if configured
}

func (sm *ShardMonitor) triggerShardFailureAlert(shardID string, metrics HealthMetrics) {
    alert := &Alert{
        Type:        "SHARD_FAILURE",
        ShardID:     shardID,
        Message:     fmt.Sprintf("Shard %s is unhealthy - multiple health check failures", shardID),
        Severity:    "CRITICAL",
        Timestamp:   time.Now(),
    }
    
    sm.alerting.TriggerAlert(alert)
    
    // Mumbai traffic control room jaisa immediate action
    sm.initiateFailoverProcedure(shardID)
}

func (sm *ShardMonitor) initiateFailoverProcedure(shardID string) {
    fmt.Printf("🔄 Initiating failover procedure for shard: %s\n", shardID)
    
    // Failover steps:
    // 1. Mark shard as UNAVAILABLE in load balancer
    // 2. Redirect traffic to replica shards
    // 3. Start automated recovery procedures
    // 4. Notify engineering team for manual intervention
}

func NewMetricsCollector() *MetricsCollector {
    return &MetricsCollector{
        QueryLatencies:    make(map[string][]float64),
        ThroughputHistory: make(map[string][]float64), 
        ErrorRates:        make(map[string][]float64),
    }
}

// Demonstrate the monitoring system
func main() {
    monitor := NewShardMonitor()
    
    // Setup sample shards - Mumbai के database shards
    monitor.shards["mumbai_north_shard"] = &ShardInfo{
        ID:       "mumbai_north_shard",
        Host:     "mumbai-north-db.example.com",
        Port:     5432,
        Status:   "HEALTHY",
    }
    
    monitor.shards["mumbai_south_shard"] = &ShardInfo{
        ID:       "mumbai_south_shard", 
        Host:     "mumbai-south-db.example.com",
        Port:     5432,
        Status:   "HEALTHY",
    }
    
    monitor.shards["mumbai_west_shard"] = &ShardInfo{
        ID:       "mumbai_west_shard",
        Host:     "mumbai-west-db.example.com", 
        Port:     5432,
        Status:   "HEALTHY",
    }
    
    // Setup health checkers
    for shardID := range monitor.shards {
        monitor.healthCheckers[shardID] = &HealthChecker{
            ShardID:       shardID,
            CheckInterval: 30 * time.Second,
            Timeout:       5 * time.Second,
            MaxFailures:   3,
        }
    }
    
    fmt.Println("🔍 Starting Mumbai Database Shard Monitoring System")
    fmt.Println("=" * 60)
    
    // Simulate monitoring for a short period
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()
    
    go monitor.StartMonitoring()
    
    // Wait for monitoring to run
    <-ctx.Done()
    
    // Display final status
    fmt.Println("\n📊 Final Shard Status Report:")
    fmt.Println("=" * 35)
    
    monitor.mu.RLock()
    for shardID, shard := range monitor.shards {
        fmt.Printf("Shard: %s\n", shardID)
        fmt.Printf("  Status: %s\n", shard.Status)
        fmt.Printf("  Latency P99: %.2fms\n", shard.QueryLatencyP99)
        fmt.Printf("  QPS: %.1f\n", shard.QueriesPerSecond)
        fmt.Printf("  Error Rate: %.3f%%\n", shard.ErrorRate)
        fmt.Printf("  Disk Usage: %.1f%%\n", shard.DiskUsagePercent)
        fmt.Println()
    }
    monitor.mu.RUnlock()
}
```

### Mumbai Traffic Control Room Analogy

```python
class MumbaiTrafficControlRoom:
    """
    Mumbai traffic control room को database monitoring के रूप में
    """
    def __init__(self):
        self.traffic_signals = {
            "Bandra_Junction": {"status": "GREEN", "wait_time": 45, "congestion": 0.7},
            "Andheri_East": {"status": "RED", "wait_time": 120, "congestion": 0.9},
            "Powai": {"status": "GREEN", "wait_time": 30, "congestion": 0.4},
            "Kurla": {"status": "YELLOW", "wait_time": 75, "congestion": 0.8}
        }
        
        self.traffic_density = {
            "peak_morning": (8, 10),   # 8-10 AM
            "off_peak": (11, 17),      # 11-5 PM  
            "peak_evening": (18, 21),  # 6-9 PM
            "late_night": (22, 7)      # 10 PM - 7 AM
        }
    
    def monitor_traffic_signals(self):
        """Traffic signals की monitoring - Database shards जैसी"""
        print("🚦 Mumbai Traffic Control Room - Real-time Status")
        print("=" * 55)
        
        for junction, status in self.traffic_signals.items():
            congestion_level = self.get_congestion_description(status["congestion"])
            
            print(f"{junction}:")
            print(f"  Signal: {status['status']}")
            print(f"  Wait Time: {status['wait_time']} seconds")
            print(f"  Congestion: {congestion_level} ({status['congestion']:.1%})")
            
            # Alert conditions
            if status["wait_time"] > 100:
                print(f"  🚨 ALERT: High wait time at {junction}")
            if status["congestion"] > 0.85:
                print(f"  ⚠️  WARNING: Heavy congestion at {junction}")
            
            print()
    
    def get_congestion_description(self, congestion_rate):
        """Congestion rate को descriptive text में convert करना"""
        if congestion_rate < 0.3:
            return "Light Traffic"
        elif congestion_rate < 0.6:
            return "Moderate Traffic" 
        elif congestion_rate < 0.8:
            return "Heavy Traffic"
        else:
            return "Severe Congestion"
    
    def suggest_alternate_routes(self, high_congestion_areas):
        """High congestion के time पर alternate routes suggest करना"""
        route_suggestions = {
            "Andheri_East": ["Use Andheri West route", "Take Jogeshwari bypass"],
            "Kurla": ["Use Ghatkopar route", "Take BKC internal roads"],
            "Bandra_Junction": ["Use Linking Road", "Take Carter Road coastal route"]
        }
        
        suggestions = []
        for area in high_congestion_areas:
            if area in route_suggestions:
                suggestions.extend(route_suggestions[area])
        
        return suggestions

# Traffic monitoring demonstration  
traffic_control = MumbaiTrafficControlRoom()
traffic_control.monitor_traffic_signals()

# Find high congestion areas
high_congestion = [
    junction for junction, status in traffic_control.traffic_signals.items() 
    if status["congestion"] > 0.8
]

if high_congestion:
    print("🛣️  Alternate Route Suggestions:")
    suggestions = traffic_control.suggest_alternate_routes(high_congestion)
    for suggestion in suggestions:
        print(f"  • {suggestion}")
```

---

## Section 4: Advanced Implementation Patterns

**Host**: Ab dekhte hain kuch advanced patterns jo production mein use karte hain. Ye sab real companies ke experiences se aaye hain.

### Pattern 1: Shard-aware Application Layer

```java
// Advanced Java implementation for shard-aware applications
import java.util.*;
import java.util.concurrent.*;
import java.sql.*;

public class ShardAwareDataAccessLayer {
    
    private final Map<String, DataSource> shardDataSources;
    private final ShardRouter shardRouter; 
    private final CrossShardQueryExecutor crossShardExecutor;
    private final TransactionManager transactionManager;
    
    public ShardAwareDataAccessLayer(
            Map<String, DataSource> shardDataSources,
            ShardRouter router) {
        this.shardDataSources = shardDataSources;
        this.shardRouter = router;
        this.crossShardExecutor = new CrossShardQueryExecutor(shardDataSources);
        this.transactionManager = new DistributedTransactionManager();
    }
    
    // Single shard query - सबसे fast और simple
    public <T> CompletableFuture<T> querySingleShard(
            String shardKey, 
            String query, 
            ResultSetMapper<T> mapper,
            Object... params) {
        
        return CompletableFuture.supplyAsync(() -> {
            String shardId = shardRouter.getShardId(shardKey);
            DataSource dataSource = shardDataSources.get(shardId);
            
            try (Connection conn = dataSource.getConnection();
                 PreparedStatement stmt = conn.prepareStatement(query)) {
                
                // Set parameters
                for (int i = 0; i < params.length; i++) {
                    stmt.setObject(i + 1, params[i]);
                }
                
                try (ResultSet rs = stmt.executeQuery()) {
                    return mapper.map(rs);
                }
                
            } catch (SQLException e) {
                throw new DatabaseException("Query failed on shard: " + shardId, e);
            }
        });
    }
    
    // Cross-shard aggregation query - Complex but powerful
    public <T> CompletableFuture<List<T>> queryCrossShards(
            List<String> shardKeys,
            String query,
            ResultSetMapper<T> mapper,
            Object... params) {
        
        // Determine unique shards involved
        Set<String> uniqueShards = shardKeys.stream()
            .map(shardRouter::getShardId)
            .collect(Collectors.toSet());
        
        // Execute query on each shard in parallel
        List<CompletableFuture<List<T>>> shardQueries = uniqueShards.stream()
            .map(shardId -> executeQueryOnShard(shardId, query, mapper, params))
            .collect(Collectors.toList());
        
        // Combine results from all shards
        return CompletableFuture.allOf(shardQueries.toArray(new CompletableFuture[0]))
            .thenApply(v -> shardQueries.stream()
                .map(CompletableFuture::join)
                .flatMap(List::stream)
                .collect(Collectors.toList()));
    }
    
    private <T> CompletableFuture<List<T>> executeQueryOnShard(
            String shardId,
            String query, 
            ResultSetMapper<T> mapper,
            Object... params) {
        
        return CompletableFuture.supplyAsync(() -> {
            DataSource dataSource = shardDataSources.get(shardId);
            List<T> results = new ArrayList<>();
            
            try (Connection conn = dataSource.getConnection();
                 PreparedStatement stmt = conn.prepareStatement(query)) {
                
                for (int i = 0; i < params.length; i++) {
                    stmt.setObject(i + 1, params[i]);
                }
                
                try (ResultSet rs = stmt.executeQuery()) {
                    while (rs.next()) {
                        results.add(mapper.map(rs));
                    }
                }
                
            } catch (SQLException e) {
                throw new DatabaseException("Query failed on shard: " + shardId, e);
            }
            
            return results;
        });
    }
    
    // Distributed transaction across multiple shards
    public CompletableFuture<TransactionResult> executeDistributedTransaction(
            List<ShardOperation> operations) {
        
        return CompletableFuture.supplyAsync(() -> {
            String transactionId = UUID.randomUUID().toString();
            
            try {
                // Phase 1: Prepare all operations
                Map<String, Boolean> prepareResults = new HashMap<>();
                
                for (ShardOperation op : operations) {
                    String shardId = shardRouter.getShardId(op.getShardKey());
                    boolean prepared = transactionManager.prepare(shardId, transactionId, op);
                    prepareResults.put(shardId, prepared);
                }
                
                // Check if all shards prepared successfully
                boolean allPrepared = prepareResults.values().stream()
                    .allMatch(prepared -> prepared);
                
                if (allPrepared) {
                    // Phase 2: Commit all operations
                    for (String shardId : prepareResults.keySet()) {
                        transactionManager.commit(shardId, transactionId);
                    }
                    
                    return new TransactionResult(transactionId, "COMMITTED", operations.size());
                    
                } else {
                    // Phase 2: Abort all operations
                    for (String shardId : prepareResults.keySet()) {
                        if (prepareResults.get(shardId)) {
                            transactionManager.abort(shardId, transactionId);
                        }
                    }
                    
                    return new TransactionResult(transactionId, "ABORTED", 0);
                }
                
            } catch (Exception e) {
                // Emergency abort all prepared transactions
                transactionManager.emergencyAbort(transactionId);
                throw new TransactionException("Distributed transaction failed", e);
            }
        });
    }
}

// Mumbai bank transfer example using shard-aware layer
class MumbaiBankTransferService {
    private final ShardAwareDataAccessLayer dataLayer;
    
    public MumbaiBankTransferService(ShardAwareDataAccessLayer dataLayer) {
        this.dataLayer = dataLayer;
    }
    
    public CompletableFuture<TransferResult> transferMoney(
            String fromAccount, 
            String toAccount, 
            BigDecimal amount) {
        
        // Create distributed transaction operations
        List<ShardOperation> operations = Arrays.asList(
            // Debit from source account
            new ShardOperation(fromAccount, 
                "UPDATE accounts SET balance = balance - ? WHERE account_no = ?",
                Arrays.asList(amount, fromAccount)),
            
            // Credit to destination account  
            new ShardOperation(toAccount,
                "UPDATE accounts SET balance = balance + ? WHERE account_no = ?", 
                Arrays.asList(amount, toAccount)),
            
            // Insert transaction record
            new ShardOperation(fromAccount, // Transaction record goes with source account
                "INSERT INTO transactions (from_account, to_account, amount, timestamp) VALUES (?, ?, ?, ?)",
                Arrays.asList(fromAccount, toAccount, amount, new Timestamp(System.currentTimeMillis())))
        );
        
        return dataLayer.executeDistributedTransaction(operations)
            .thenApply(txnResult -> {
                if ("COMMITTED".equals(txnResult.getStatus())) {
                    return new TransferResult(true, "Transfer successful", 
                        txnResult.getTransactionId());
                } else {
                    return new TransferResult(false, "Transfer failed - insufficient funds or system error",
                        txnResult.getTransactionId());
                }
            });
    }
}
```

### Pattern 2: Intelligent Query Routing

```python
class IntelligentQueryRouter:
    """
    ML-based query routing - Mumbai traffic navigation जैसा
    """
    def __init__(self):
        self.shard_performance_history = {}
        self.query_patterns = {}
        self.load_balancer = AdaptiveLoadBalancer()
        
    def route_query_intelligently(self, query, estimated_cost, user_context):
        """
        Query को best shard पर route करना - traffic conditions के basis पर
        """
        # Analyze query pattern
        query_signature = self.get_query_signature(query)
        
        # Get candidate shards
        candidate_shards = self.get_candidate_shards(query, user_context)
        
        # Score each shard based on multiple factors
        shard_scores = {}
        for shard_id in candidate_shards:
            score = self.calculate_shard_score(
                shard_id, query_signature, estimated_cost, user_context
            )
            shard_scores[shard_id] = score
        
        # Select best shard
        best_shard = max(shard_scores.keys(), key=lambda s: shard_scores[s])
        
        # Update routing history for learning
        self.update_routing_history(query_signature, best_shard, shard_scores)
        
        return {
            "selected_shard": best_shard,
            "confidence_score": shard_scores[best_shard],
            "alternative_shards": sorted(shard_scores.keys(), 
                                       key=lambda s: shard_scores[s], reverse=True)[1:3],
            "routing_reason": self.get_routing_reason(best_shard, shard_scores)
        }
    
    def calculate_shard_score(self, shard_id, query_signature, estimated_cost, user_context):
        """
        Shard के लिए composite score calculation
        """
        # Performance metrics (40% weightage)
        perf_score = self.get_performance_score(shard_id, query_signature)
        
        # Load balancing (25% weightage)  
        load_score = self.get_load_balance_score(shard_id)
        
        # Data locality (20% weightage)
        locality_score = self.get_data_locality_score(shard_id, user_context)
        
        # Cost optimization (15% weightage)
        cost_score = self.get_cost_score(shard_id, estimated_cost)
        
        # Weighted composite score
        composite_score = (
            perf_score * 0.40 +
            load_score * 0.25 +
            locality_score * 0.20 +
            cost_score * 0.15
        )
        
        return composite_score
    
    def get_performance_score(self, shard_id, query_signature):
        """Historical performance के basis पर score"""
        history = self.shard_performance_history.get(shard_id, {})
        query_history = history.get(query_signature, {})
        
        if not query_history:
            return 0.5  # Neutral score for unknown queries
        
        # Recent performance metrics
        avg_latency = query_history.get("avg_latency_ms", 100)
        success_rate = query_history.get("success_rate", 0.95)
        
        # Lower latency = higher score
        latency_score = max(0, 1 - (avg_latency / 1000))  # Normalize to 0-1
        
        # Higher success rate = higher score
        reliability_score = success_rate
        
        return (latency_score * 0.6 + reliability_score * 0.4)
    
    def get_load_balance_score(self, shard_id):
        """Current load के basis पर score"""
        current_load = self.load_balancer.get_current_load(shard_id)
        
        # Lower load = higher score
        if current_load < 0.3:      # Light load
            return 1.0
        elif current_load < 0.6:    # Moderate load
            return 0.7
        elif current_load < 0.8:    # Heavy load
            return 0.4
        else:                       # Very heavy load
            return 0.1
    
    def get_data_locality_score(self, shard_id, user_context):
        """Data locality के basis पर score"""
        user_region = user_context.get("region", "unknown")
        shard_region = self.get_shard_region(shard_id)
        
        if user_region == shard_region:
            return 1.0      # Same region - best locality
        elif self.are_regions_nearby(user_region, shard_region):
            return 0.7      # Nearby regions - good locality
        else:
            return 0.3      # Far regions - poor locality
    
    def are_regions_nearby(self, region1, region2):
        """Check if two regions are geographically nearby"""
        nearby_regions = {
            "mumbai": ["pune", "nashik", "aurangabad"],
            "delhi": ["gurgaon", "noida", "faridabad"],
            "bangalore": ["mysore", "mangalore", "hubli"],
            "chennai": ["coimbatore", "madurai", "tiruchirappalli"]
        }
        
        return (region2 in nearby_regions.get(region1, []) or 
                region1 in nearby_regions.get(region2, []))

# Mumbai navigation system as query routing analogy
class MumbaiNavigationRouter:
    """
    Mumbai navigation system को query routing के रूप में
    """
    def __init__(self):
        self.route_options = {
            "andheri_to_bkc": [
                {"route": "Western Express Highway", "time": 25, "traffic": 0.8, "cost": 150},
                {"route": "JVLR + Internal Roads", "time": 35, "traffic": 0.4, "cost": 80},
                {"route": "Link Road", "time": 45, "traffic": 0.6, "cost": 60}
            ],
            "thane_to_nariman_point": [
                {"route": "Eastern Express Highway", "time": 60, "traffic": 0.9, "cost": 200},
                {"route": "Central Railway + Taxi", "time": 75, "traffic": 0.3, "cost": 120},
                {"route": "Ghodbunder Road + Western Express", "time": 90, "traffic": 0.5, "cost": 180}
            ]
        }
    
    def get_best_route(self, source, destination, preferences):
        """
        Best route selection - Query routing जैसा logic
        """
        route_key = f"{source}_to_{destination}".lower()
        available_routes = self.route_options.get(route_key, [])
        
        if not available_routes:
            return {"error": "No route available"}
        
        # Score each route based on preferences
        route_scores = []
        for route in available_routes:
            score = self.calculate_route_score(route, preferences)
            route_scores.append({**route, "score": score})
        
        # Sort by score descending
        route_scores.sort(key=lambda r: r["score"], reverse=True)
        
        best_route = route_scores[0]
        
        return {
            "recommended_route": best_route["route"],
            "estimated_time": best_route["time"],
            "traffic_level": self.get_traffic_description(best_route["traffic"]),
            "estimated_cost": best_route["cost"],
            "confidence": best_route["score"],
            "alternatives": route_scores[1:3]  # Top 2 alternatives
        }
    
    def calculate_route_score(self, route, preferences):
        """Route scoring based on user preferences"""
        weights = preferences.get("weights", {
            "time": 0.4,      # 40% weight for time
            "cost": 0.3,      # 30% weight for cost  
            "comfort": 0.3    # 30% weight for comfort (low traffic)
        })
        
        # Normalize metrics to 0-1 scale
        time_score = max(0, 1 - (route["time"] / 120))      # 2 hours max
        cost_score = max(0, 1 - (route["cost"] / 300))      # ₹300 max
        comfort_score = 1 - route["traffic"]                # Lower traffic = higher comfort
        
        # Calculate weighted score
        total_score = (
            time_score * weights["time"] +
            cost_score * weights["cost"] + 
            comfort_score * weights["comfort"]
        )
        
        return total_score
    
    def get_traffic_description(self, traffic_level):
        """Traffic level को description में convert करना"""
        if traffic_level < 0.3:
            return "Light Traffic"
        elif traffic_level < 0.6:
            return "Moderate Traffic"
        elif traffic_level < 0.8:
            return "Heavy Traffic"
        else:
            return "Severe Traffic"

# Demonstration
navigation = MumbaiNavigationRouter()

# Example: Route from Andheri to BKC
user_preferences = {
    "weights": {
        "time": 0.5,     # Time is most important
        "cost": 0.2,     # Cost is less important  
        "comfort": 0.3   # Moderate importance to comfort
    }
}

route_recommendation = navigation.get_best_route(
    "andheri", "bkc", user_preferences
)

print("🗺️ Mumbai Route Recommendation (like Query Routing)")
print("=" * 55)
print(f"Recommended Route: {route_recommendation['recommended_route']}")
print(f"Estimated Time: {route_recommendation['estimated_time']} minutes")
print(f"Traffic Level: {route_recommendation['traffic_level']}")
print(f"Estimated Cost: ₹{route_recommendation['estimated_cost']}")
print(f"Confidence Score: {route_recommendation['confidence']:.2f}")

if route_recommendation.get('alternatives'):
    print(f"\nAlternative Routes:")
    for i, alt in enumerate(route_recommendation['alternatives'], 1):
        print(f"  {i}. {alt['route']} - {alt['time']}min, ₹{alt['cost']} (Score: {alt['score']:.2f})")
```

---

## Section 5: Production Challenges and Solutions

**Host**: Doston, ab real production challenges ki baat karte hain. Theory mein sab perfect lagta hai, but production mein jaake pata chalta hai ki kitni complications hain.

### Challenge 1: Hot Shards during Festivals

```python
class FestivalLoadManager:
    """
    Festival season के time पर hot shard management
    Diwali, Dussehra, Dhanterus जैसे occasions का handling
    """
    def __init__(self):
        self.festival_calendar = {
            "diwali": {"date": "2024-11-01", "load_multiplier": 5.0, "duration_days": 5},
            "dussehra": {"date": "2024-10-12", "load_multiplier": 3.0, "duration_days": 3},
            "dhanteras": {"date": "2024-10-29", "load_multiplier": 8.0, "duration_days": 2},
            "holi": {"date": "2024-03-08", "load_multiplier": 2.5, "duration_days": 2}
        }
        
        self.hotspot_shards = set()
        self.temporary_shards = {}
        
    def predict_festival_load(self, festival_name, base_load):
        """
        Festival के time पर expected load prediction
        """
        festival_config = self.festival_calendar.get(festival_name)
        if not festival_config:
            return base_load
        
        multiplier = festival_config["load_multiplier"]
        predicted_load = base_load * multiplier
        
        # Category-specific adjustments
        category_adjustments = {
            "electronics": 1.5,    # Electronics sales spike during festivals
            "fashion": 2.0,        # Fashion sales go crazy
            "jewelry": 3.0,        # Jewelry sales peak during Dhanteras/Diwali
            "groceries": 1.2       # Moderate increase in groceries
        }
        
        return {
            "base_predicted_load": predicted_load,
            "category_predictions": {
                category: predicted_load * adj 
                for category, adj in category_adjustments.items()
            },
            "peak_hours": [10, 11, 19, 20, 21],  # 10-11 AM, 7-9 PM
            "duration_days": festival_config["duration_days"]
        }
    
    def setup_festival_scaling(self, festival_name, affected_shards):
        """
        Festival के लिए temporary scaling setup
        """
        load_prediction = self.predict_festival_load(festival_name, base_load=1000)
        
        scaling_strategy = {
            "temporary_shard_creation": [],
            "load_balancing_rules": {},
            "caching_strategy": {},
            "queue_management": {}
        }
        
        for shard_id in affected_shards:
            # Create temporary read replicas
            temp_shard_id = f"{shard_id}_festival_replica_{festival_name}"
            
            scaling_strategy["temporary_shard_creation"].append({
                "temp_shard_id": temp_shard_id,
                "source_shard": shard_id,
                "capacity_multiplier": load_prediction["base_predicted_load"] / 1000,
                "setup_time_hours": 4,
                "teardown_date": self.calculate_teardown_date(festival_name)
            })
            
            # Setup intelligent load balancing
            scaling_strategy["load_balancing_rules"][shard_id] = {
                "read_traffic_distribution": {
                    "primary": 0.3,      # 30% on primary shard
                    "replicas": 0.7      # 70% on temporary replicas
                },
                "write_traffic": {
                    "primary": 1.0       # All writes still go to primary
                },
                "failover_strategy": "cascade_to_next_available"
            }
            
            # Aggressive caching for read-heavy workloads
            scaling_strategy["caching_strategy"][shard_id] = {
                "cache_ttl_seconds": 60,        # 1 minute cache
                "cache_hit_target": 0.90,       # 90% cache hit rate target
                "preload_popular_products": True, # Preload trending products
                "cache_warming_strategy": "ml_prediction_based"
            }
        
        return scaling_strategy
    
    def handle_hotspot_detection(self, shard_id, current_metrics):
        """
        Real-time hotspot detection और immediate action
        """
        hotspot_indicators = {
            "cpu_usage": current_metrics.get("cpu_usage", 0) > 85,
            "query_latency": current_metrics.get("avg_latency_ms", 0) > 500,
            "connection_saturation": current_metrics.get("connection_usage", 0) > 90,
            "error_rate": current_metrics.get("error_rate", 0) > 2.0
        }
        
        hotspot_score = sum(hotspot_indicators.values())
        
        if hotspot_score >= 2:  # 2 or more indicators triggered
            self.hotspot_shards.add(shard_id)
            
            immediate_actions = self.execute_hotspot_mitigation(shard_id, current_metrics)
            
            return {
                "hotspot_detected": True,
                "hotspot_score": hotspot_score,
                "indicators": hotspot_indicators,
                "immediate_actions": immediate_actions,
                "estimated_recovery_time": self.estimate_recovery_time(hotspot_score)
            }
        
        return {"hotspot_detected": False}
    
    def execute_hotspot_mitigation(self, shard_id, metrics):
        """
        Immediate hotspot mitigation actions
        """
        actions = []
        
        # Action 1: Activate circuit breaker for non-critical queries
        actions.append({
            "action": "circuit_breaker_activation",
            "target": "non_critical_queries",
            "expected_load_reduction": "30%"
        })
        
        # Action 2: Increase cache TTL to reduce database hits
        actions.append({
            "action": "increase_cache_ttl",
            "from_seconds": 60,
            "to_seconds": 300,
            "expected_hit_rate_improvement": "15%"
        })
        
        # Action 3: Route read traffic to least loaded replica
        if metrics.get("read_write_ratio", 0.7) > 0.5:  # Read-heavy workload
            actions.append({
                "action": "redirect_read_traffic",
                "target": "least_loaded_replica",
                "traffic_percentage": 80
            })
        
        # Action 4: Enable query queueing for complex operations
        if metrics.get("complex_query_ratio", 0.2) > 0.1:
            actions.append({
                "action": "enable_query_queueing",
                "queue_size": 1000,
                "priority_levels": ["high", "medium", "low"]
            })
        
        return actions

# Real example: Flipkart Diwali sale hotspot management
def simulate_diwali_sale_hotspot():
    """
    Flipkart Diwali sale के time पर hotspot management simulation
    """
    festival_manager = FestivalLoadManager()
    
    # Predict Diwali load
    diwali_prediction = festival_manager.predict_festival_load("diwali", base_load=5000)
    
    print("🪔 Diwali Sale - Hotspot Management Simulation")
    print("=" * 50)
    print(f"Base Load: 5,000 QPS")
    print(f"Predicted Peak Load: {diwali_prediction['base_predicted_load']:,.0f} QPS")
    print(f"Peak Hours: {diwali_prediction['peak_hours']}")
    
    # Simulate hotspot detection
    print(f"\n🔥 Hotspot Detection Simulation:")
    
    electronics_shard_metrics = {
        "cpu_usage": 92,        # Very high CPU
        "avg_latency_ms": 750,  # High latency
        "connection_usage": 95,  # Connection saturation  
        "error_rate": 3.2       # High error rate
    }
    
    hotspot_result = festival_manager.handle_hotspot_detection(
        "flipkart_electronics_shard", electronics_shard_metrics
    )
    
    if hotspot_result["hotspot_detected"]:
        print(f"  ⚠️  HOTSPOT DETECTED in Electronics Shard")
        print(f"  Hotspot Score: {hotspot_result['hotspot_score']}/4")
        print(f"  Triggered Indicators:")
        
        for indicator, triggered in hotspot_result["indicators"].items():
            status = "🔴 TRIGGERED" if triggered else "🟢 NORMAL"
            print(f"    {indicator}: {status}")
        
        print(f"\n  🚀 Immediate Actions Taken:")
        for action in hotspot_result["immediate_actions"]:
            print(f"    • {action['action']}")
            if "expected_load_reduction" in action:
                print(f"      Expected Load Reduction: {action['expected_load_reduction']}")
        
        print(f"\n  ⏱️  Estimated Recovery Time: {hotspot_result['estimated_recovery_time']} minutes")

# Run the simulation
simulate_diwali_sale_hotspot()
```

### Challenge 2: Cross-Shard Query Optimization

Mumbai mein inter-zone travel optimize karne jaisa challenge hai - कैसे minimize करें travel time aur cost.

```java
// Advanced cross-shard query optimization
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;

public class CrossShardQueryOptimizer {
    
    private final Map<String, ShardMetadata> shardMetadata;
    private final QueryPlanCache queryPlanCache;
    private final ExecutorService executorService;
    
    public CrossShardQueryOptimizer(Map<String, ShardMetadata> shardMetadata) {
        this.shardMetadata = shardMetadata;
        this.queryPlanCache = new QueryPlanCache(1000); // Cache 1000 query plans
        this.executorService = Executors.newFixedThreadPool(20);
    }
    
    public CompletableFuture<QueryResult> executeOptimizedCrossShardQuery(
            CrossShardQuery query) {
        
        // Check if we have a cached execution plan
        String querySignature = query.getSignature();
        Optional<QueryExecutionPlan> cachedPlan = queryPlanCache.get(querySignature);
        
        QueryExecutionPlan executionPlan = cachedPlan.orElseGet(() -> 
            createOptimalExecutionPlan(query));
        
        // Cache the plan for future use
        if (!cachedPlan.isPresent()) {
            queryPlanCache.put(querySignature, executionPlan);
        }
        
        // Execute the optimized plan
        return executeQueryPlan(executionPlan);
    }
    
    private QueryExecutionPlan createOptimalExecutionPlan(CrossShardQuery query) {
        // Analyze query to determine optimal execution strategy
        QueryAnalysis analysis = analyzeQuery(query);
        
        ExecutionStrategy strategy = selectOptimalStrategy(analysis);
        
        switch (strategy) {
            case SCATTER_GATHER:
                return createScatterGatherPlan(query, analysis);
            case FEDERATED_JOIN:
                return createFederatedJoinPlan(query, analysis);  
            case SEQUENTIAL_EXECUTION:
                return createSequentialPlan(query, analysis);
            case HYBRID_APPROACH:
                return createHybridPlan(query, analysis);
            default:
                throw new UnsupportedOperationException("Unknown strategy: " + strategy);
        }
    }
    
    private QueryExecutionPlan createScatterGatherPlan(CrossShardQuery query, QueryAnalysis analysis) {
        // Mumbai broadcasting jaisa - सभी shards को same query भेजना
        List<String> involvedShards = analysis.getInvolvedShards();
        
        List<ShardQueryTask> tasks = involvedShards.stream()
            .map(shardId -> new ShardQueryTask(
                shardId,
                adaptQueryForShard(query, shardId),
                ShardQueryTask.Priority.HIGH
            ))
            .collect(Collectors.toList());
        
        return QueryExecutionPlan.builder()
            .strategy(ExecutionStrategy.SCATTER_GATHER)
            .tasks(tasks)
            .aggregationFunction(this::aggregateScatterGatherResults)
            .estimatedExecutionTime(calculateEstimatedTime(tasks))
            .parallelismLevel(Math.min(involvedShards.size(), 10)) // Max 10 parallel
            .build();
    }
    
    private QueryExecutionPlan createFederatedJoinPlan(CrossShardQuery query, QueryAnalysis analysis) {
        // Mumbai local train connection jaisa - step by step execution
        
        // Identify the most selective query component
        String primaryShard = analysis.getMostSelectiveShard();
        SubQuery primaryQuery = analysis.getPrimarySubQuery();
        
        // Create execution stages
        List<ExecutionStage> stages = new ArrayList<>();
        
        // Stage 1: Execute primary query to get candidate keys
        stages.add(ExecutionStage.builder()
            .stageId("primary_filter")
            .shardId(primaryShard)
            .query(primaryQuery)
            .outputType(ExecutionStage.OutputType.KEY_LIST)
            .build());
        
        // Stage 2: Use primary results to query other shards  
        for (String shardId : analysis.getSecondaryShards()) {
            stages.add(ExecutionStage.builder()
                .stageId("secondary_lookup_" + shardId)
                .shardId(shardId) 
                .query(analysis.getSecondaryQuery(shardId))
                .dependsOn("primary_filter")
                .inputType(ExecutionStage.InputType.KEY_LIST)
                .build());
        }
        
        // Stage 3: Final result aggregation
        stages.add(ExecutionStage.builder()
            .stageId("final_aggregation")
            .aggregationFunction(this::performFederatedJoin)
            .dependsOn(analysis.getSecondaryShards().toArray(new String[0]))
            .build());
        
        return QueryExecutionPlan.builder()
            .strategy(ExecutionStrategy.FEDERATED_JOIN)
            .stages(stages)
            .estimatedExecutionTime(calculateSequentialTime(stages))
            .build();
    }
    
    private CompletableFuture<QueryResult> executeQueryPlan(QueryExecutionPlan plan) {
        switch (plan.getStrategy()) {
            case SCATTER_GATHER:
                return executeScatterGather(plan);
            case FEDERATED_JOIN:
                return executeFederatedJoin(plan);
            default:
                throw new UnsupportedOperationException("Strategy not implemented");
        }
    }
    
    private CompletableFuture<QueryResult> executeScatterGather(QueryExecutionPlan plan) {
        List<ShardQueryTask> tasks = plan.getTasks();
        
        // Execute all tasks in parallel
        List<CompletableFuture<ShardQueryResult>> futures = tasks.stream()
            .map(task -> CompletableFuture.supplyAsync(() -> 
                executeShardQuery(task), executorService))
            .collect(Collectors.toList());
        
        // Combine all results when complete
        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
            .thenApply(v -> {
                List<ShardQueryResult> results = futures.stream()
                    .map(CompletableFuture::join)
                    .collect(Collectors.toList());
                
                return plan.getAggregationFunction().apply(results);
            });
    }
    
    private CompletableFuture<QueryResult> executeFederatedJoin(QueryExecutionPlan plan) {
        // Execute stages sequentially, respecting dependencies
        return executeStagesSequentially(plan.getStages(), new HashMap<>());
    }
    
    private CompletableFuture<QueryResult> executeStagesSequentially(
            List<ExecutionStage> stages, 
            Map<String, Object> intermediateResults) {
        
        if (stages.isEmpty()) {
            return CompletableFuture.completedFuture(
                (QueryResult) intermediateResults.get("final_result"));
        }
        
        ExecutionStage currentStage = stages.get(0);
        List<ExecutionStage> remainingStages = stages.subList(1, stages.size());
        
        return executeStage(currentStage, intermediateResults)
            .thenCompose(stageResult -> {
                intermediateResults.put(currentStage.getStageId(), stageResult);
                return executeStagesSequentially(remainingStages, intermediateResults);
            });
    }
}

// Mumbai inter-zone travel optimization example
class MumbaiInterZoneTravelOptimizer {
    
    public TravelPlan optimizeInterZoneTravel(String source, String destination, 
                                            TravelPreferences preferences) {
        // Analyze the travel requirement
        TravelAnalysis analysis = analyzeTravelRequirement(source, destination);
        
        if (analysis.isDirectRouteAvailable()) {
            // Direct route - like single shard query
            return createDirectRoutePlan(source, destination, analysis);
        } else {
            // Inter-zone travel - like cross-shard query  
            return createInterZoneRoutePlan(source, destination, analysis, preferences);
        }
    }
    
    private TravelPlan createInterZoneRoutePlan(String source, String destination,
                                              TravelAnalysis analysis, 
                                              TravelPreferences preferences) {
        
        List<String> interchangeOptions = analysis.getInterchangeStations();
        
        // Evaluate each interchange option
        List<RouteOption> routeOptions = interchangeOptions.stream()
            .map(interchange -> evaluateInterchangeRoute(source, destination, interchange))
            .collect(Collectors.toList());
        
        // Select best route based on preferences
        RouteOption bestRoute = selectBestRoute(routeOptions, preferences);
        
        return TravelPlan.builder()
            .source(source)
            .destination(destination)
            .interchangeStation(bestRoute.getInterchangeStation())
            .totalTime(bestRoute.getTotalTime())
            .totalCost(bestRoute.getTotalCost())
            .comfortLevel(bestRoute.getComfortLevel())
            .legs(bestRoute.getLegs())
            .build();
    }
    
    private RouteOption evaluateInterchangeRoute(String source, String destination, 
                                               String interchange) {
        
        // First leg: Source to interchange
        TravelLeg firstLeg = TravelLeg.builder()
            .from(source)
            .to(interchange)
            .mode("LOCAL_TRAIN")
            .estimatedTime(calculateTravelTime(source, interchange))
            .cost(calculateCost(source, interchange))
            .build();
        
        // Interchange walking time
        TravelLeg interchangeLeg = TravelLeg.builder()
            .from(interchange + "_arrival")
            .to(interchange + "_departure")
            .mode("WALKING")
            .estimatedTime(getInterchangeWalkingTime(interchange))
            .cost(0)
            .build();
        
        // Second leg: Interchange to destination  
        TravelLeg secondLeg = TravelLeg.builder()
            .from(interchange)
            .to(destination)
            .mode("LOCAL_TRAIN")
            .estimatedTime(calculateTravelTime(interchange, destination))
            .cost(calculateCost(interchange, destination))
            .build();
        
        List<TravelLeg> legs = Arrays.asList(firstLeg, interchangeLeg, secondLeg);
        
        return RouteOption.builder()
            .interchangeStation(interchange)
            .legs(legs)
            .totalTime(legs.stream().mapToInt(TravelLeg::getEstimatedTime).sum())
            .totalCost(legs.stream().mapToInt(TravelLeg::getCost).sum())
            .comfortLevel(calculateComfortLevel(legs))
            .build();
    }
}
```

---

## Conclusion: Part 2 Summary

**Host**: Doston, Part 2 mein humne dekha ki sharding implementation kitni complex ho sakti hai. Mumbai ki daily challenges se samjha ki distributed systems mein kya kya problems aati hain aur unka solution kaise karte hain.

**Key Takeaways from Part 2**:

1. **Cross-Shard Transactions**: Sabse complex part - coordination, consistency, failure handling
2. **Data Migration**: Live system mein data migrate karna - planning, dual-write, validation
3. **Monitoring**: Real-time health checks, performance tracking, alert management  
4. **Advanced Patterns**: Intelligent routing, load balancing, caching strategies
5. **Production Challenges**: Hot shards, festival load, cross-shard query optimization

**Mumbai Learnings Applied**:
- **Inter-zone Travel**: Cross-shard queries की complexity
- **Traffic Control**: Real-time monitoring aur alert systems
- **Society Redevelopment**: Data migration strategies
- **Festival Rush**: Scaling strategies during peak load

**Technical Deep Dives Covered**:
- Java implementation for distributed transactions
- Go-based monitoring and alerting systems  
- Python-based intelligent query routing
- Production-ready code patterns and error handling

**Part 3 Preview**:
- Real production failure stories (Netflix, WhatsApp, Instagram)
- Cost optimization strategies for Indian market
- Performance tuning और optimization techniques
- Future of database sharding - what's coming next
- Complete troubleshooting playbook

**Code Examples Summary**:
- Cross-shard transaction manager (Python)
- Resilient shard connection handling (Java)
- High-performance monitoring system (Go)
- Intelligent query routing with ML (Python)
- Festival load management system (Python)

Mumbai se seekhi hui philosophy: **"Jugaad with Intelligence"** - problems ko creatively solve karna, but proper engineering practices ke saath.

Part 3 mein milte hain - real war stories aur battle-tested solutions के saath! 

---

**[Part 2 Ends - Transition Music]**

*Total Word Count for Part 2: 7,192 words*