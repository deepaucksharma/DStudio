# DynamoDB Design Guide

## Problem Statement and Overview

DynamoDB is Amazon's fully managed NoSQL database service designed to provide predictable performance at any scale. It was built to address the limitations of traditional relational databases in distributed systems, particularly for applications requiring:

- **Single-digit millisecond latency** at any scale
- **Unlimited throughput and storage** with seamless scaling
- **High availability** (99.999% for global tables)
- **Built-in security, backup, and restore** capabilities

### Key Design Goals

1. **Predictable Performance**: Consistent performance regardless of dataset size
2. **Seamless Scalability**: Automatic scaling without downtime
3. **High Availability**: Multi-AZ replication within regions
4. **Flexible Data Model**: Support for document and key-value workloads
5. **Cost Optimization**: Pay only for what you use with on-demand pricing

## Scale Metrics and Performance Characteristics

### Performance Metrics

```mermaid
graph TD
    A[DynamoDB Performance] --> B[Latency]
    A --> C[Throughput]
    A --> D[Storage]
    
    B --> B1[Single-digit ms reads]
    B --> B2[Single-digit ms writes]
    B --> B3[<100μs with DAX]
    
    C --> C1[40K RCU per table]
    C --> C2[40K WCU per table]
    C --> C3[Auto-scaling available]
    
    D --> D1[No practical limit]
    D --> D2[10GB per partition]
    D --> D3[400KB item size limit]
```

### Scale Numbers

- **Tables**: Unlimited per account
- **Items per table**: No limit
- **Item size**: 400KB maximum
- **Throughput**: 
  - Read: 40,000 RCU per table (80,000 with eventual consistency)
  - Write: 40,000 WCU per table
  - Burst capacity: 300 seconds of unused capacity
- **Global Secondary Indexes**: 20 per table
- **Local Secondary Indexes**: 5 per table

### SLA Guarantees

- **Regional tables**: 99.99% availability
- **Global tables**: 99.999% availability
- **Durability**: 99.999999999% (11 9's)

## Architecture with Partitioning and Replication

### High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        C1[Application]
        C2[SDK/CLI]
        C3[DAX Client]
    end
    
    subgraph "API Layer"
        A1[Request Router]
        A2[Authentication]
        A3[Rate Limiting]
    end
    
    subgraph "Storage Layer"
        S1[Partition 1]
        S2[Partition 2]
        S3[Partition N]
    end
    
    subgraph "Replication"
        R1[Primary]
        R2[Secondary 1]
        R3[Secondary 2]
    end
    
    C1 --> A1
    C2 --> A1
    C3 --> A1
    
    A1 --> S1
    A1 --> S2
    A1 --> S3
    
    S1 --> R1
    R1 --> R2
    R1 --> R3
```

### Partitioning Strategy

DynamoDB automatically partitions data based on:

1. **Partition Key Hash**: Uses consistent hashing to distribute items
2. **Throughput Requirements**: Creates partitions based on provisioned capacity
3. **Storage Requirements**: Splits partitions when approaching 10GB

```python
# Partition calculation
def calculate_partitions(table_config):
# Based on throughput
    read_partitions = ceil(provisioned_RCU / 3000)
    write_partitions = ceil(provisioned_WCU / 1000)
    throughput_partitions = max(read_partitions, write_partitions)
    
# Based on storage
    storage_partitions = ceil(table_size_gb / 10)
    
# Total partitions
    return max(throughput_partitions, storage_partitions)
```

### Replication Architecture

```mermaid
sequenceDiagram
    participant Client
    participant Router
    participant Primary
    participant Secondary1
    participant Secondary2
    
    Client->>Router: Write Request
    Router->>Primary: Forward Write
    Primary->>Primary: Write to Log
    Primary-->>Router: Acknowledge
    Router-->>Client: Success Response
    
    Note over Primary,Secondary2: Asynchronous Replication
    Primary->>Secondary1: Replicate
    Primary->>Secondary2: Replicate
```

## Consistent Hashing Implementation

### Hash Ring Design

```python
class ConsistentHashRing:
    def __init__(self, nodes, virtual_nodes=150):
        self.nodes = nodes
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self._build_ring()
    
    def _hash(self, key):
        """MD5 hash function for consistent distribution"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def _build_ring(self):
        """Build hash ring with virtual nodes"""
        for node in self.nodes:
            for i in range(self.virtual_nodes):
                virtual_key = f"{node}:{i}"
                hash_value = self._hash(virtual_key)
                self.ring[hash_value] = node
        
# Sort for binary search
        self.sorted_keys = sorted(self.ring.keys())
    
    def get_node(self, key):
        """Find node responsible for key"""
        if not self.ring:
            return None
            
        hash_value = self._hash(key)
        
# Binary search for next node
        idx = bisect_right(self.sorted_keys, hash_value)
        if idx == len(self.sorted_keys):
            idx = 0
            
        return self.ring[self.sorted_keys[idx]]
```

### Partition Key Distribution

```python
def calculate_partition(partition_key, num_partitions):
    """Calculate which partition an item belongs to"""
# DynamoDB uses internal hash function
    hash_value = internal_hash(partition_key)
    
# Map to partition
    partition = hash_value % num_partitions
    
    return partition
```

## Data Model and API Design

### Table Design

```python
# Single Table Design Pattern
table_schema = {
    "TableName": "ApplicationData",
    "KeySchema": [
        {
            "AttributeName": "PK",  # Partition Key
            "KeyType": "HASH"
        },
        {
            "AttributeName": "SK",  # Sort Key
            "KeyType": "RANGE"
        }
    ],
    "AttributeDefinitions": [
        {"AttributeName": "PK", "AttributeType": "S"},
        {"AttributeName": "SK", "AttributeType": "S"},
        {"AttributeName": "GSI1PK", "AttributeType": "S"},
        {"AttributeName": "GSI1SK", "AttributeType": "S"}
    ],
    "GlobalSecondaryIndexes": [
        {
            "IndexName": "GSI1",
            "Keys": [
                {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                {"AttributeName": "GSI1SK", "KeyType": "RANGE"}
            ],
            "Projection": {"ProjectionType": "ALL"}
        }
    ]
}
```

### Access Patterns

```python
# Example: E-commerce Application
class DynamoDBPatterns:
    def __init__(self, table):
        self.table = table
    
# Pattern 1: Get user by ID
    def get_user(self, user_id):
        return self.table.get_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'USER#{user_id}'
            }
        )
    
# Pattern 2: Get user orders
    def get_user_orders(self, user_id):
        return self.table.query(
            KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
            ExpressionAttributeValues={
                ':pk': f'USER#{user_id}',
                ':sk': 'ORDER#'
            }
        )
    
# Pattern 3: Get order by ID
    def get_order(self, order_id):
        return self.table.query(
            IndexName='GSI1',
            KeyConditionExpression='GSI1PK = :pk',
            ExpressionAttributeValues={
                ':pk': f'ORDER#{order_id}'
            }
        )
```

### API Operations

```python
# Core API operations
class DynamoDBAPI:
# Item operations
    def put_item(self, item, condition_expression=None):
        """Create or replace an item"""
        params = {'Item': item}
        if condition_expression:
            params['ConditionExpression'] = condition_expression
        return self.table.put_item(**params)
    
    def update_item(self, key, update_expression, condition_expression=None):
        """Update specific attributes"""
        params = {
            'Key': key,
            'UpdateExpression': update_expression,
            'ReturnValues': 'ALL_NEW'
        }
        if condition_expression:
            params['ConditionExpression'] = condition_expression
        return self.table.update_item(**params)
    
# Batch operations
    def batch_write(self, items, batch_size=25):
        """Write multiple items efficiently"""
        with self.table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
    
# Transaction operations
    def transact_write(self, actions):
        """ACID transactions across items"""
        return self.client.transact_write_items(
            TransactItems=actions
        )
```

## Performance Optimizations

### 1. Partition Key Design

```python
# Hot partition prevention
class PartitionKeyStrategies:
    @staticmethod
    def add_suffix(key, suffix_range=100):
        """Distribute load across partitions"""
        suffix = random.randint(0, suffix_range - 1)
        return f"{key}#{suffix}"
    
    @staticmethod
    def time_based_partition(key, time_bucket_minutes=5):
        """Partition by time for time-series data"""
        current_bucket = int(time.time() / (time_bucket_minutes * 60))
        return f"{key}#{current_bucket}"
```

### 2. Query Optimization

```python
# Efficient query patterns
class QueryOptimization:
    def paginated_query(self, partition_key, page_size=100):
        """Implement pagination for large result sets"""
        paginator = self.table.meta.client.get_paginator('query')
        
        pages = paginator.paginate(
            TableName=self.table.name,
            KeyConditionExpression='PK = :pk',
            ExpressionAttributeValues={':pk': partition_key},
            PaginationConfig={'PageSize': page_size}
        )
        
        for page in pages:
            yield page['Items']
    
    def parallel_scan(self, total_segments=4):
        """Parallel scanning for large tables"""
        with ThreadPoolExecutor(max_workers=total_segments) as executor:
            futures = []
            
            for segment in range(total_segments):
                future = executor.submit(
                    self._scan_segment,
                    segment,
                    total_segments
                )
                futures.append(future)
            
            for future in as_completed(futures):
                yield future.result()
```

### 3. Caching Strategy

```python
# DAX integration
class DynamoDBWithCache:
    def __init__(self, table_name, dax_endpoint=None):
        if dax_endpoint:
            self.client = AmazonDaxClient(endpoints=[dax_endpoint])
        else:
            self.client = boto3.client('dynamodb')
        
        self.table_name = table_name
        self.cache_ttl = 300  # 5 minutes
    
    def get_item_cached(self, key):
        """Get item with DAX caching"""
        response = self.client.get_item(
            TableName=self.table_name,
            Key=key,
            ConsistentRead=False  # Use eventual consistency for caching
        )
        return response.get('Item')
```

### 4. Write Optimization

```python
# Burst capacity management
class WriteOptimizer:
    def __init__(self, table, write_capacity):
        self.table = table
        self.write_capacity = write_capacity
        self.token_bucket = TokenBucket(write_capacity)
    
    def write_with_backoff(self, item):
        """Write with exponential backoff"""
        max_retries = 3
        base_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                if self.token_bucket.consume(1):
                    return self.table.put_item(Item=item)
                else:
                    time.sleep(base_delay * (2 ** attempt))
            except ProvisionedThroughputExceededException:
                if attempt == max_retries - 1:
                    raise
                time.sleep(base_delay * (2 ** attempt))
```

## Cost Considerations

### Pricing Model Components

```python
class DynamoDBCostCalculator:
    def __init__(self):
# Pricing per region (us-east-1 example)
        self.pricing = {
            'on_demand': {
                'write_request': 1.25e-6,  # per request
                'read_request': 0.25e-6,    # per request
                'storage_gb': 0.25          # per GB/month
            },
            'provisioned': {
                'wcu_hour': 0.00065,        # per WCU/hour
                'rcu_hour': 0.00013,        # per RCU/hour
                'storage_gb': 0.25          # per GB/month
            }
        }
    
    def calculate_monthly_cost(self, config):
        """Calculate monthly cost based on usage"""
        if config['billing_mode'] == 'ON_DEMAND':
            cost = (
                config['write_requests'] * self.pricing['on_demand']['write_request'] +
                config['read_requests'] * self.pricing['on_demand']['read_request'] +
                config['storage_gb'] * self.pricing['on_demand']['storage_gb']
            )
        else:  # PROVISIONED
            hours_per_month = 730
            cost = (
                config['wcu'] * self.pricing['provisioned']['wcu_hour'] * hours_per_month +
                config['rcu'] * self.pricing['provisioned']['rcu_hour'] * hours_per_month +
                config['storage_gb'] * self.pricing['provisioned']['storage_gb']
            )
        
# Add costs for GSIs, backups, etc.
        return cost
```

### Cost Optimization Strategies

1. **Use On-Demand for Variable Workloads**
   ```python
# Switch between billing modes based on usage patterns
   def optimize_billing_mode(usage_pattern):
       if usage_pattern.is_predictable and usage_pattern.baseline_high:
           return "PROVISIONED"
       else:
           return "ON_DEMAND"
   ```

2. **Optimize Data Storage**
   ```python
# Compress large attributes
   def compress_item(item):
       for key, value in item.items():
           if isinstance(value, str) and len(value) > 1000:
               item[key] = gzip.compress(value.encode())
       return item
   ```

3. **Efficient TTL Usage**
   ```python
# Automatic data expiration
   def set_ttl(item, days_to_live=30):
       ttl_timestamp = int(time.time() + (days_to_live * 86400))
       item['ttl'] = ttl_timestamp
       return item
   ```

## Common Interview Questions

### System Design Questions

1. **Design a shopping cart system using DynamoDB**
   ```python
# Key design decisions:
# - Single table design
# - Session-based carts with TTL
# - Optimistic locking for concurrent updates
   
   cart_schema = {
       'PK': 'USER#userId',
       'SK': 'CART#sessionId',
       'items': [
           {'productId': 'P123', 'quantity': 2, 'price': 29.99}
       ],
       'version': 1,  # For optimistic locking
       'ttl': 1234567890  # Auto-expire abandoned carts
   }
   ```

2. **Design a real-time leaderboard**
   ```python
# Challenges:
# - Hot partition on popular games
# - Real-time updates
# - Global and friend leaderboards
   
   leaderboard_patterns = {
       'global_score': {
           'PK': 'GAME#gameId#SHARD#shardId',
           'SK': 'SCORE#paddedScore#userId'
       },
       'user_scores': {
           'PK': 'USER#userId',
           'SK': 'GAME#gameId'
       }
   }
   ```

### Technical Deep-Dives

1. **How does DynamoDB handle hot partitions?**
   - Adaptive capacity automatically redistributes throughput
   - Contributor Insights identifies hot keys
   - Best practice: Design for uniform distribution

2. **Explain eventual consistency in DynamoDB**
   - Read after write may not reflect latest data
   - Typically consistent within 1 second
   - Use consistent reads when necessary (2x RCU cost)

3. **How do Global Tables work?**
   ```mermaid
   graph TB
       subgraph "Region 1"
           T1[Table Replica 1]
           S1[DynamoDB Streams]
       end
       
       subgraph "Region 2"
           T2[Table Replica 2]
           S2[DynamoDB Streams]
       end
       
       T1 --> S1
       S1 --> T2
       T2 --> S2
       S2 --> T1
   ```

### Performance Scenarios

1. **Handling traffic spikes**
   ```python
# Auto-scaling configuration
   auto_scaling_config = {
       'target_tracking': {
           'metric': 'ConsumedReadCapacityUnits',
           'target_value': 70.0,  # 70% utilization
           'scale_in_cooldown': 60,
           'scale_out_cooldown': 60
       },
       'min_capacity': 5,
       'max_capacity': 40000
   }
   ```

2. **Optimizing for large item collections**
   ```python
# Item collection size limit: 10GB
# Solution: Distribute across multiple partitions
   
   def shard_large_collection(user_id, shard_count=10):
       shard = hash(user_id) % shard_count
       return f"USER#{user_id}#SHARD#{shard}"
   ```

### Architecture Trade-offs

1. **DynamoDB vs Aurora**
   - DynamoDB: NoSQL, horizontal scaling, predictable performance
   - Aurora: SQL, ACID, complex queries, joins

2. **When NOT to use DynamoDB**
   - Complex queries requiring joins
   - Full-text search requirements
   - Strong consistency across all operations
   - Ad-hoc analytical queries

### Best Practices Checklist

- [ ] Design partition keys for uniform distribution
- [ ] Use sort keys for one-to-many relationships
- [ ] Implement error handling with exponential backoff
- [ ] Monitor CloudWatch metrics for hot partitions
- [ ] Use batch operations for bulk writes
- [ ] Enable point-in-time recovery for critical tables
- [ ] Implement item-level TTL for data lifecycle
- [ ] Use DAX for microsecond latency requirements
- [ ] Design for eventual consistency by default
- [ ] Test failover scenarios with global tables

### Common Pitfalls

1. **Hot Partitions**: Uneven key distribution
2. **Large Items**: Approaching 400KB limit
3. **Inefficient Queries**: Not using indexes properly
4. **Over-provisioning**: Not using auto-scaling
5. **Ignoring Costs**: Not monitoring usage patterns