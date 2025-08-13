# Episode 21: CQRS/Event Sourcing Code Examples

## Overview
यह directory contains production-ready code examples for CQRS (Command Query Responsibility Segregation) और Event Sourcing patterns। ये examples Indian context में real-world scenarios को demonstrate करते हैं।

## Code Examples Summary

### Python Examples

#### 1. Basic CQRS Pattern (`python/01_basic_cqrs_pattern.py`)
- **Description**: Flipkart order processing के लिए basic CQRS implementation
- **Features**:
  - Command and Query segregation
  - Order creation और status updates
  - Separate read/write models
  - Event-driven architecture
- **Usage**:
  ```bash
  python python/01_basic_cqrs_pattern.py
  ```

#### 2. Event Store with PostgreSQL (`python/02_event_store_postgresql.py`)
- **Description**: Paytm wallet transactions के लिए production-ready Event Store
- **Features**:
  - PostgreSQL-based event storage
  - Optimistic concurrency control
  - Event replay capabilities
  - Snapshot support for performance
- **Dependencies**:
  ```bash
  pip install psycopg2-binary
  ```
- **Usage**:
  ```bash
  python python/02_event_store_postgresql.py
  ```

#### 3. Command Handlers (`python/03_command_handlers_flipkart.py`)
- **Description**: Flipkart order management के लिए comprehensive command handlers
- **Features**:
  - Business logic centralization
  - Validation और error handling
  - Inventory management
  - Payment processing
  - Command bus pattern
- **Usage**:
  ```bash
  python python/03_command_handlers_flipkart.py
  ```

#### 4. Query Handlers (`python/04_query_handlers_status_lookup.py`)
- **Description**: Order status और tracking के लिए optimized query handlers
- **Features**:
  - Denormalized read models
  - Fast order lookups
  - Customer history analysis
  - Search capabilities
- **Usage**:
  ```bash
  python python/04_query_handlers_status_lookup.py
  ```

### Java Examples

#### 1. Event Sourcing Bank Account (`java/EventSourcingBankAccount.java`)
- **Description**: Indian banking system के लिए complete Event Sourcing implementation
- **Features**:
  - Banking domain events
  - Account state reconstruction
  - Event replay mechanism
  - Audit trail capabilities
- **Compilation**:
  ```bash
  cd java/
  javac EventSourcingBankAccount.java
  java EventSourcingBankAccount
  ```

## Requirements

### Python Dependencies
```bash
pip install psycopg2-binary asyncio dataclasses
```

### Java Dependencies
```bash
# No external dependencies required for basic examples
# Production versions would use Spring Boot, JPA, etc.
```

## Key Concepts Demonstrated

### CQRS (Command Query Responsibility Segregation)
1. **Command Side**: Write operations के लिए optimized
   - Business logic validation
   - State changes
   - Event generation

2. **Query Side**: Read operations के लिए optimized
   - Denormalized views
   - Fast data retrieval
   - Complex queries

### Event Sourcing
1. **Event Storage**: सभी changes को events के रूप में store करना
2. **State Reconstruction**: Events से current state rebuild करना
3. **Temporal Queries**: Historical data analysis
4. **Audit Trail**: Complete change history

## Indian Context Examples

### Banking Domain
- UPI transactions
- Account management
- Fraud detection
- Compliance reporting

### E-commerce Domain
- Flipkart order processing
- Inventory management
- Payment systems
- Customer analytics

### Fintech Domain
- Paytm wallet operations
- Transaction monitoring
- Risk assessment
- Regulatory compliance

## Production Considerations

### Performance Optimizations
1. **Snapshots**: Periodic state snapshots for faster reconstruction
2. **Caching**: Read model caching for better query performance
3. **Indexing**: Proper database indexing strategies
4. **Partitioning**: Event store partitioning for scalability

### Scaling Strategies
1. **Read Replicas**: Multiple read databases for query load distribution
2. **Event Partitioning**: Partition events by aggregate ID
3. **CQRS Scaling**: Independent scaling of read and write sides
4. **Microservices**: Domain-specific command/query services

### Data Consistency
1. **Eventual Consistency**: Accept temporary inconsistencies
2. **Compensating Actions**: Handle failed operations
3. **Saga Pattern**: Manage distributed transactions
4. **Event Ordering**: Ensure proper event sequence

## Running Examples

```bash
# Python examples
python python/01_basic_cqrs_pattern.py
python python/02_event_store_postgresql.py
python python/03_command_handlers_flipkart.py
python python/04_query_handlers_status_lookup.py

# Java examples
cd java/
javac EventSourcingBankAccount.java
java EventSourcingBankAccount
```

## Troubleshooting

### Common Issues
1. **Concurrency Conflicts**: Use optimistic locking
2. **Performance Issues**: Add snapshots and caching
3. **Data Consistency**: Implement proper event ordering
4. **Scalability**: Use partitioning and replication

### Monitoring
1. **Event Processing Latency**: Track command-to-event time
2. **Query Performance**: Monitor read model response times
3. **Event Store Health**: Track storage and retrieval metrics
4. **Business Metrics**: Monitor domain-specific KPIs

## Further Reading

### Books
- "Implementing Domain-Driven Design" by Vaughn Vernon
- "Building Event-Driven Microservices" by Adam Bellemare
- "Microservices Patterns" by Chris Richardson

### Online Resources
- Event Sourcing patterns
- CQRS implementation guides
- Domain-driven design principles

## Contributing

When adding new examples:
1. Follow Indian context scenarios
2. Include comprehensive error handling
3. Add proper documentation
4. Include test cases
5. Consider production scalability