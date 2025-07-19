# Change Data Capture (CDC)

**Every change leaves a trace**

## THE PROBLEM

```
Keeping systems in sync is hard:
- Batch ETL = stale data (hours old)
- Dual writes = inconsistency risk
- Polling = resource waste
- Point-to-point sync = spaghetti

How to stream changes reliably?
```

## THE SOLUTION

```
CDC: Capture database changes as events

Database Write → Transaction Log → CDC Process → Event Stream
                                        ↓
                                  [Subscribers]
                                  - Search Index
                                  - Cache
                                  - Analytics
                                  - Other Services
```

## CDC Patterns

```
1. LOG-BASED CDC (Most reliable)
   Read DB transaction log directly
   
2. TRIGGER-BASED CDC
   Database triggers on INSERT/UPDATE/DELETE
   
3. QUERY-BASED CDC
   Poll with timestamp/version columns
   
4. SNAPSHOT + LOG
   Initial snapshot + incremental changes
```

## IMPLEMENTATION

```python
# Log-based CDC implementation
class LogBasedCDC:
    def __init__(self, database_config):
        self.db_config = database_config
        self.last_log_position = self.load_checkpoint()
        self.handlers = {}
        
    def capture_changes(self):
        """Read database transaction log"""
        
        # Connect to database replication stream
        with ReplicationConnection(self.db_config) as conn:
            # Start from last known position
            conn.start_replication(self.last_log_position)
            
            for log_entry in conn.stream_log():
                try:
                    # Parse log entry
                    change = self.parse_log_entry(log_entry)
                    
                    # Process change
                    self.process_change(change)
                    
                    # Update checkpoint
                    self.last_log_position = log_entry.position
                    self.save_checkpoint()
                    
                except Exception as e:
                    self.handle_error(e, log_entry)
    
    def parse_log_entry(self, log_entry):
        """Parse different log formats"""
        
        if log_entry.type == 'INSERT':
            return Change(
                operation='INSERT',
                table=log_entry.table,
                data=log_entry.new_values,
                timestamp=log_entry.timestamp,
                transaction_id=log_entry.tx_id
            )
            
        elif log_entry.type == 'UPDATE':
            return Change(
                operation='UPDATE',
                table=log_entry.table,
                before=log_entry.old_values,
                after=log_entry.new_values,
                timestamp=log_entry.timestamp,
                transaction_id=log_entry.tx_id
            )
            
        elif log_entry.type == 'DELETE':
            return Change(
                operation='DELETE',
                table=log_entry.table,
                data=log_entry.old_values,
                timestamp=log_entry.timestamp,
                transaction_id=log_entry.tx_id
            )
    
    def process_change(self, change):
        """Route change to handlers"""
        
        # Table-specific handlers
        if change.table in self.handlers:
            for handler in self.handlers[change.table]:
                handler.handle(change)
                
        # Global handlers
        for handler in self.handlers.get('*', []):
            handler.handle(change)

# Debezium-style CDC connector
class CDCConnector:
    def __init__(self, source_config, sink_config):
        self.source = self.create_source(source_config)
        self.sink = self.create_sink(sink_config)
        self.transformers = []
        self.filters = []
        
    def add_transformer(self, transformer):
        """Add data transformation"""
        self.transformers.append(transformer)
        
    def add_filter(self, filter_fn):
        """Add change filter"""
        self.filters.append(filter_fn)
        
    async def run(self):
        """Main CDC pipeline"""
        
        async for change in self.source.stream():
            # Apply filters
            if not all(f(change) for f in self.filters):
                continue
                
            # Apply transformations
            transformed = change
            for transformer in self.transformers:
                transformed = transformer.transform(transformed)
                
            # Send to sink
            await self.sink.send(transformed)
            
            # Commit position
            await self.source.commit(change.position)

# Snapshot + incremental CDC
class SnapshotCDC:
    def __init__(self, database, target):
        self.database = database
        self.target = target
        self.snapshot_completed = False
        
    async def sync(self):
        """Full sync with snapshot + incremental"""
        
        if not self.snapshot_completed:
            await self.initial_snapshot()
            
        await self.incremental_sync()
    
    async def initial_snapshot(self):
        """Take consistent snapshot"""
        
        # Start transaction for consistency
        async with self.database.transaction() as tx:
            # Get current log position
            log_position = await tx.get_current_log_position()
            
            # Mark target as "snapshotting"
            await self.target.begin_snapshot()
            
            # Copy all tables
            for table in self.database.tables:
                await self.snapshot_table(tx, table)
                
            # Save log position for incremental
            await self.target.save_snapshot_position(log_position)
            
            # Mark snapshot complete
            await self.target.complete_snapshot()
            self.snapshot_completed = True
    
    async def snapshot_table(self, tx, table):
        """Stream table data in batches"""
        
        total_rows = await tx.count(table)
        batch_size = 10000
        
        for offset in range(0, total_rows, batch_size):
            rows = await tx.query(
                f"SELECT * FROM {table} LIMIT {batch_size} OFFSET {offset}"
            )
            
            await self.target.write_batch(table, rows)
            
            # Report progress
            progress = min(100, (offset + batch_size) / total_rows * 100)
            print(f"Snapshot {table}: {progress:.1f}%")

# Schema evolution handling
class SchemaEvolutionHandler:
    def __init__(self):
        self.schema_registry = SchemaRegistry()
        
    def handle_change(self, change):
        """Handle schema changes gracefully"""
        
        # Detect schema change
        if change.operation == 'ALTER_TABLE':
            old_schema = self.schema_registry.get(change.table)
            new_schema = change.new_schema
            
            # Generate migration
            migration = self.generate_migration(old_schema, new_schema)
            
            # Apply to downstream systems
            self.apply_migration(migration)
            
            # Update registry
            self.schema_registry.update(change.table, new_schema)
    
    def generate_migration(self, old_schema, new_schema):
        """Generate migration for downstream"""
        
        migration = Migration()
        
        # Added columns
        for col in new_schema.columns:
            if col not in old_schema.columns:
                migration.add_column(col, default=self.infer_default(col))
                
        # Removed columns  
        for col in old_schema.columns:
            if col not in new_schema.columns:
                migration.drop_column(col)
                
        # Changed columns
        for col in new_schema.columns:
            if col in old_schema.columns:
                old_type = old_schema.columns[col].type
                new_type = new_schema.columns[col].type
                if old_type != new_type:
                    migration.alter_column(col, new_type)
                    
        return migration

# CDC to multiple targets
class CDCFanOut:
    def __init__(self, source):
        self.source = source
        self.targets = []
        self.failed_targets = {}
        
    def add_target(self, target, retry_policy=None):
        self.targets.append({
            'target': target,
            'retry_policy': retry_policy or ExponentialBackoff()
        })
        
    async def process(self):
        """Fan out changes to all targets"""
        
        async for change in self.source.stream():
            # Send to all targets in parallel
            tasks = []
            for target_config in self.targets:
                task = self.send_with_retry(target_config, change)
                tasks.append(task)
                
            # Wait for all to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle failures
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    await self.handle_target_failure(
                        self.targets[i], change, result
                    )
    
    async def send_with_retry(self, target_config, change):
        """Send change with retry logic"""
        
        target = target_config['target']
        retry_policy = target_config['retry_policy']
        
        for attempt in range(retry_policy.max_attempts):
            try:
                await target.send(change)
                return
            except Exception as e:
                if attempt < retry_policy.max_attempts - 1:
                    await asyncio.sleep(retry_policy.get_delay(attempt))
                else:
                    raise

# CDC monitoring
class CDCMonitor:
    def __init__(self):
        self.metrics = {
            'changes_captured': Counter(),
            'changes_processed': Counter(),
            'lag_seconds': Gauge(),
            'errors': Counter()
        }
        
    def record_change(self, change):
        self.metrics['changes_captured'].inc()
        
        # Calculate replication lag
        lag = time.time() - change.timestamp
        self.metrics['lag_seconds'].set(lag)
        
    def record_error(self, error, change):
        self.metrics['errors'].inc()
        
        # Alert if lag is too high
        if self.metrics['lag_seconds'].value > 60:
            self.alert(f"CDC lag high: {lag}s")
```

## ✓ CHOOSE THIS WHEN:
• Real-time data synchronization needed
• Event sourcing from existing databases
• Building CQRS read models
• Cache invalidation requirements
• Microservices data integration

## ⚠️ BEWARE OF:
• Initial snapshot can be expensive
• Schema evolution complexity
• Out-of-order delivery
• Handling deletes properly
• CDC tool operational overhead

## REAL EXAMPLES
• **LinkedIn**: Databus CDC for real-time data
• **Netflix**: CDC for cache updates
• **Uber**: Database replication via CDC