---
title: Change Data Capture (CDC)
description: How to stream changes reliably?
```text
type: pattern
difficulty: intermediate
reading_time: 10 min
prerequisites: []
pattern_type: "general"
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part III: Patterns](/patterns/) → **Change Data Capture (CDC)**

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
```bash
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
```bash
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
```bash
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

---

**Previous**: [← Caching Strategies](caching-strategies.md) | **Next**: [Circuit Breaker Pattern →](circuit-breaker.md)
---

## ✅ When to Use

### Ideal Scenarios
- **Distributed systems** with external dependencies
- **High-availability services** requiring reliability
- **External service integration** with potential failures
- **High-traffic applications** needing protection

### Environmental Factors
- **High Traffic**: System handles significant load
- **External Dependencies**: Calls to other services or systems
- **Reliability Requirements**: Uptime is critical to business
- **Resource Constraints**: Limited connections, threads, or memory

### Team Readiness
- Team understands distributed systems concepts
- Monitoring and alerting infrastructure exists
- Operations team can respond to pattern-related alerts

### Business Context
- Cost of downtime is significant
- User experience is a priority
- System is customer-facing or business-critical

## ❌ When NOT to Use

### Inappropriate Scenarios
- **Simple applications** with minimal complexity
- **Development environments** where reliability isn't critical
- **Single-user systems** without scale requirements
- **Internal tools** with relaxed availability needs

### Technical Constraints
- **Simple Systems**: Overhead exceeds benefits
- **Development/Testing**: Adds unnecessary complexity
- **Performance Critical**: Pattern overhead is unacceptable
- **Legacy Systems**: Cannot be easily modified

### Resource Limitations
- **No Monitoring**: Cannot observe pattern effectiveness
- **Limited Expertise**: Team lacks distributed systems knowledge
- **Tight Coupling**: System design prevents pattern implementation

### Anti-Patterns
- Adding complexity without clear benefit
- Implementing without proper monitoring
- Using as a substitute for fixing root causes
- Over-engineering simple problems

## ⚖️ Trade-offs

### Benefits vs Costs

| Benefit | Cost | Mitigation |
|---------|------|------------|
| **Improved Reliability** | Implementation complexity | Use proven libraries/frameworks |
| **Better Performance** | Resource overhead | Monitor and tune parameters |
| **Faster Recovery** | Operational complexity | Invest in monitoring and training |
| **Clearer Debugging** | Additional logging | Use structured logging |

### Performance Impact
- **Latency**: Small overhead per operation
- **Memory**: Additional state tracking
- **CPU**: Monitoring and decision logic
- **Network**: Possible additional monitoring calls

### Operational Complexity
- **Monitoring**: Need dashboards and alerts
- **Configuration**: Parameters must be tuned
- **Debugging**: Additional failure modes to understand
- **Testing**: More scenarios to validate

### Development Trade-offs
- **Initial Cost**: More time to implement correctly
- **Maintenance**: Ongoing tuning and monitoring
- **Testing**: Complex failure scenarios to validate
- **Documentation**: More concepts for team to understand

## 💻 Code Sample

### Basic Implementation

```python
class CdcPattern:
    def __init__(self, config):
        self.config = config
        self.metrics = Metrics()
        self.state = "ACTIVE"

    def process(self, request):
        """Main processing logic with pattern protection"""
        if not self._is_healthy():
            return self._fallback(request)

        try:
            result = self._protected_operation(request)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure(e)
            return self._fallback(request)

    def _is_healthy(self):
        """Check if the protected resource is healthy"""
        return self.metrics.error_rate < self.config.threshold

    def _protected_operation(self, request):
        """The operation being protected by this pattern"""
        # Implementation depends on specific use case
        pass

    def _fallback(self, request):
        """Fallback behavior when protection activates"""
        return {"status": "fallback", "message": "Service temporarily unavailable"}

    def _record_success(self):
        self.metrics.record_success()

    def _record_failure(self, error):
        self.metrics.record_failure(error)

# Usage example
pattern = CdcPattern(config)
result = pattern.process(user_request)
```

### Configuration Example

```yaml
cdc:
  enabled: true
  thresholds:
    failure_rate: 50%
    response_time: 5s
    error_count: 10
  timeouts:
    operation: 30s
    recovery: 60s
  fallback:
    enabled: true
    strategy: "cached_response"
  monitoring:
    metrics_enabled: true
    health_check_interval: 30s
```

### Testing the Implementation

```python
def test_cdc_behavior():
    pattern = CdcPattern(test_config)

    # Test normal operation
    result = pattern.process(normal_request)
    assert result['status'] == 'success'

    # Test failure handling
    with mock.patch('external_service.call', side_effect=Exception):
        result = pattern.process(failing_request)
        assert result['status'] == 'fallback'

    # Test recovery
    result = pattern.process(normal_request)
    assert result['status'] == 'success'
```

## 💪 Hands-On Exercises

### Exercise 1: Pattern Recognition ⭐⭐
**Time**: ~15 minutes
**Objective**: Identify Change Data Capture (CDC) in existing systems

**Task**:
Find 2 real-world examples where Change Data Capture (CDC) is implemented:
1. **Example 1**: A well-known tech company or service
2. **Example 2**: An open-source project or tool you've used

For each example:
- Describe how the pattern is implemented
- What problems it solves in that context
- What alternatives could have been used

### Exercise 2: Implementation Planning ⭐⭐⭐
**Time**: ~25 minutes
**Objective**: Design an implementation of Change Data Capture (CDC)

**Scenario**: You need to implement Change Data Capture (CDC) for an e-commerce checkout system processing 10,000 orders/hour.

**Requirements**:
- 99.9% availability required
- Payment processing must be reliable
- Orders must not be lost or duplicated

**Your Task**:
1. Design the architecture using Change Data Capture (CDC)
2. Identify key components and their responsibilities
3. Define interfaces between components
4. Consider failure scenarios and mitigation strategies

**Deliverable**: Architecture diagram + 1-page implementation plan

### Exercise 3: Trade-off Analysis ⭐⭐⭐⭐
**Time**: ~20 minutes
**Objective**: Evaluate when NOT to use Change Data Capture (CDC)

**Challenge**: You're consulting for a startup building their first product.

**Analysis Required**:
1. **Context Assessment**: Under what conditions would Change Data Capture (CDC) be overkill?
2. **Cost-Benefit**: Compare implementation costs vs. benefits
3. **Alternatives**: What simpler approaches could work initially?
4. **Evolution Path**: How would you migrate to Change Data Capture (CDC) later?

**Anti-Pattern Warning**: Identify one common mistake teams make when implementing this pattern.

---

## 🛠️ Code Challenge

### Beginner: Basic Implementation
Implement a minimal version of Change Data Capture (CDC) in your preferred language.
- Focus on core functionality
- Include basic error handling
- Add simple logging

### Intermediate: Production Features
Extend the basic implementation with:
- Configuration management
- Metrics collection
- Unit tests
- Documentation

### Advanced: Performance & Scale
Optimize for production use:
- Handle concurrent access
- Implement backpressure
- Add monitoring hooks
- Performance benchmarks

---

## 🎯 Real-World Application

**Project Integration**:
- How would you introduce Change Data Capture (CDC) to an existing system?
- What migration strategy would minimize risk?
- How would you measure success?

**Team Discussion Points**:
1. When team members suggest this pattern, what questions should you ask?
2. How would you explain the value to non-technical stakeholders?
3. What monitoring would indicate the pattern is working well?

---
