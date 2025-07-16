Page 54: Change Data Capture
The database's transaction log is a gold mine
THE PROBLEM
Getting data out of databases:
- Polling is inefficient
- Triggers add latency
- Dual writes risk inconsistency
- Batch exports are delayed
THE SOLUTION
Tail the transaction log:

Database → Transaction Log → CDC Connector → Stream
   ↓              ↓                ↓           ↓
Updates      Every Change    Parse & Filter  Kafka
CDC Patterns:
1. LOG-BASED CDC
   MySQL binlog → Debezium → Kafka
   PostgreSQL WAL → Logical decoding
   MongoDB oplog → Change streams

2. QUERY-BASED CDC
   SELECT * WHERE updated > last_sync
   (Fallback for legacy systems)

3. TRIGGER-BASED CDC
   Database triggers → Queue
   (Higher latency, simpler setup)
PSEUDO CODE IMPLEMENTATION
CDCConnector:
    connect_to_database():
        // Start from last position
        position = load_checkpoint()
        
        if not position:
            // Initial snapshot
            position = start_snapshot()
            stream_full_table_data()
            
        // Stream changes
        for change in tail_transaction_log(position):
            process_change(change)
            save_checkpoint(change.position)
    
    process_change(change):
        // Parse database-specific format
        parsed = parse_log_entry(change)
        
        // Transform to common format
        event = {
            'operation': parsed.type,  // INSERT/UPDATE/DELETE
            'table': parsed.table,
            'key': parsed.primary_key,
            'before': parsed.old_values,
            'after': parsed.new_values,
            'timestamp': parsed.commit_time,
            'position': parsed.log_position
        }
        
        // Apply filters
        if should_capture(event):
            emit_to_stream(event)

SchemaEvolution:
    handle_schema_change(ddl_event):
        // Schema changes are events too
        if ddl_event.type == 'ADD_COLUMN':
            update_schema_registry(ddl_event)
            set_default_for_existing(ddl_event.column)
            
        elif ddl_event.type == 'DROP_COLUMN':
            mark_column_deprecated(ddl_event.column)
            continue_with_warning()
            
        elif ddl_event.type == 'RENAME_TABLE':
            create_alias_mapping(ddl_event)

DownstreamProcessor:
    // Example: Search index updater
    consume_cdc_stream():
        for batch in kafka_consumer.poll():
            bulk_updates = []
            
            for event in batch:
                if event.operation == 'DELETE':
                    bulk_updates.append(
                        delete_from_index(event.key)
                    )
                else:
                    bulk_updates.append(
                        upsert_to_index(event.key, event.after)
                    )
                    
            elasticsearch.bulk(bulk_updates)
            kafka_consumer.commit()
CDC Use Cases:
1. CACHE INVALIDATION
   DB change → CDC → Redis DEL key

2. SEARCH INDEX UPDATE
   DB change → CDC → Elasticsearch update

3. DATA WAREHOUSE SYNC
   OLTP → CDC → Transform → OLAP

4. MICROSERVICE SYNC
   Order DB → CDC → Inventory service

5. AUDIT TRAIL
   Any change → CDC → Immutable audit log
✓ CHOOSE THIS WHEN:

Need real-time data sync
Building CQRS read models
Maintaining derived data
Zero-downtime migrations
Creating audit trails

⚠️ BEWARE OF:

Initial snapshot impact
Schema evolution complexity
Log retention policies
Ordering guarantees
CDC tool maturity varies

REAL EXAMPLES

LinkedIn: Databus CDC system
Airbnb: MySQL to data warehouse
Netflix: Cassandra CDC for indexes
