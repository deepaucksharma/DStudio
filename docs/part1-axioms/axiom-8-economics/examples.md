# Economics Examples & Case Studies

!!! info "Prerequisites"
    - [Axiom 8: Economics Core Concepts](index.md)

!!! tip "Quick Navigation"
    [← Economics Concepts](index.md) | 
    [Exercises →](exercises.md) |
    [↑ Axioms Overview](../index.md)

## Real-World Cost Disasters

<div class="failure-vignette">

### 🎬 The $72,000 Cloud Bill

```yaml
Company: Small startup (anonymous)
Date: February 2020
Normal bill: $800/month
Surprise bill: $72,000

What happened:
- Developer testing data pipeline
- Forgot to set S3 lifecycle policy
- Script had retry logic with bug
- Each retry downloaded full dataset
- Running on EC2 instance in different region

The cascade:
Day 1: Script fails, retries every minute
- Downloads 1TB from S3 (different region)
- Cross-region transfer: $0.02/GB = $20
- Fails, retries: 60 × $20 = $1,200/day

Day 30: Developer returns from vacation
- Total transfer: 1,800TB
- Transfer cost: $36,000
- NAT Gateway cost: $33,000 (!)
- API requests: $3,000

Lessons learned:
1. NAT Gateway costs $0.045/GB
2. Cross-region transfer adds up
3. Retry logic needs exponential backoff
4. Set billing alerts
5. Use cost allocation tags

Prevention:
- Billing alerts at 2×, 5×, 10× normal
- VPC endpoints for S3 (avoid NAT)
- Process data in same region
- Circuit breakers on retry logic
```

</div>

<div class="failure-vignette">

### 🎬 The Firebase Bankruptcy

```yaml
Company: Social media startup
Date: October 2018
Incident: Near bankruptcy from database costs

Background:
- Using Firebase Realtime Database
- Pricing: $5/GB stored, $1/GB downloaded
- App shows user feed with images
- 100K active users

The mistake:
// Original code
db.ref('posts').on('value', (snapshot) => {
  // This downloads ALL posts EVERY time
  displayPosts(snapshot.val());
});

What happened:
- Each user opens app 10×/day
- Each open downloads all posts (50MB)
- 100K users × 10 × 50MB = 50TB/day
- Daily cost: $50,000 (!!)
- Monthly projection: $1.5M

Emergency fix:
// Pagination with limits
db.ref('posts')
  .orderByChild('timestamp')
  .limitToLast(20)
  .on('value', (snapshot) => {
    displayPosts(snapshot.val());
  });

Results:
- Reduced download to 1MB per session
- Daily cost: $1,000 (98% reduction)
- Implemented caching
- Final cost: $200/day

Lessons:
1. Understand pricing model
2. Implement pagination early
3. Cache aggressively
4. Monitor usage metrics
5. Load test with cost projection
```

</div>

<div class="failure-vignette">

### 🎬 The Kubernetes Money Pit

```yaml
Company: E-commerce platform
Date: 2021-2022
Problem: K8s cluster costs exceeding revenue

Initial setup:
- 3 environments (dev, staging, prod)
- 3 regions for "high availability"
- Node autoscaling "for safety"
- Every service gets its own namespace

The multiplication:
Base need: 10 nodes for production
× 3 (multi-AZ) = 30 nodes
× 3 (regions) = 90 nodes  
× 3 (environments) = 270 nodes
× 1.5 (autoscaling headroom) = 405 nodes
× $72/node/month = $29,160/month

Additional costs discovered:
- Load balancers: $25 × 50 = $1,250/month
- Persistent volumes: 10TB × $0.10 = $1,000/month
- Network transfer: $5,000/month
- Logging/monitoring: $8,000/month
- Total: $44,410/month

Actual usage analysis:
- Dev: 5% utilized (used 9-5 weekdays)
- Staging: 10% utilized (weekly deploys)
- Prod: 35% utilized (over-provisioned)
- Regional traffic: 95% from one region

Cost optimization:
1. Dev/staging: Scale to zero at night
2. Single region + CDN (same latency)
3. Proper resource requests/limits
4. Spot instances for non-critical
5. Reserved instances for baseline

New cost: $8,500/month (81% reduction)
```

</div>

## Hidden Cost Patterns

### 1. The Logging Tax

```yaml
Scenario: Microservices with "good" logging

Per service:
- Application logs: 10GB/day
- Access logs: 5GB/day  
- Debug logs: 20GB/day
- Audit logs: 2GB/day
Total: 37GB/day/service

With 50 microservices:
- Volume: 1.85TB/day
- CloudWatch Logs ingestion: $0.50/GB
- Daily cost: $925
- Monthly cost: $27,750
- Yearly cost: $333,000

Just for logs nobody reads!

Solution implemented:
1. Log levels by environment
   - Prod: ERROR and above
   - Staging: INFO and above
   - Dev: DEBUG (local only)

2. Structured logging with sampling
   - Sample INFO logs: 1%
   - Sample DEBUG: 0.1%
   - Keep all ERROR/FATAL

3. Local aggregation
   - Count similar logs
   - Send summaries

Result: 95% reduction in volume
New cost: $1,388/month
```

### 2. The Multi-Region Mirage

```yaml
Company belief: "We need multi-region for reliability"

Actual analysis:
- 99% of traffic from US East
- 0.8% from US West  
- 0.2% from Europe

Multi-region setup:
- 3 regions fully replicated
- Cross-region replication
- Regional load balancers
- Cost: $45,000/month

Actual outage analysis:
- Application bugs: 45%
- Deployment issues: 30%
- Configuration errors: 15%
- AWS region failures: 0%
- Network issues: 10%

Single region + CDN:
- Primary region: US East
- CloudFront for static assets
- Route 53 health checks
- Cost: $12,000/month

Reliability impact: None
Cost savings: $33,000/month (73%)
```

### 3. The Database Sprawl

```yaml
Evolution of database costs:

Month 1: "We need a database"
- RDS PostgreSQL: $200/month

Month 6: "We need caching"
- + ElastiCache Redis: $150/month

Month 12: "We need search"  
- + Elasticsearch: $500/month

Month 18: "We need analytics"
- + Redshift: $1,000/month

Month 24: "We need time series"
- + TimeStream: $300/month

Month 30: "We need graph queries"
- + Neptune: $600/month

Total: $2,750/month
Actual usage: 20% of capacity

Consolidation approach:
- PostgreSQL with extensions
  - Full text search (not Elasticsearch)
  - Time series (TimescaleDB)
  - JSON for document store
- Redis for all caching
- ClickHouse for analytics

New cost: $800/month
Savings: $1,950/month (71%)
```

## Cost Architecture Patterns

### Pattern 1: The Request Coalescing Pattern

```python
# Expensive: Every request hits database
@app.route('/api/user/<user_id>')
def get_user(user_id):
    return db.query(f"SELECT * FROM users WHERE id = {user_id}")
    # Cost: $0.0001 per request
    # 1M requests/day = $100/day

# Optimized: Batch and cache
class UserService:
    def __init__(self):
        self.batch = []
        self.cache = TTLCache(maxsize=10000, ttl=300)
        
    async def get_user(self, user_id):
        # Check cache first
        if user_id in self.cache:
            return self.cache[user_id]
            
        # Add to batch
        future = asyncio.Future()
        self.batch.append((user_id, future))
        
        # Process batch every 10ms or 100 items
        if len(self.batch) >= 100:
            await self._process_batch()
            
        return await future
        
    async def _process_batch(self):
        user_ids = [item[0] for item in self.batch]
        
        # One query for many users
        users = db.query(f"""
            SELECT * FROM users 
            WHERE id IN ({','.join(user_ids)})
        """)
        
        # Cache and resolve futures
        for user in users:
            self.cache[user.id] = user
            
        # Cost: $0.0001 per batch
        # 1M requests/day = 10K batches = $1/day
        # Savings: 99%
```

### Pattern 2: The Edge Computing Pattern

```yaml
Traditional: All processing in main region

Request flow:
1. User in Asia → US East server (200ms)
2. Process request (50ms)
3. Response → User (200ms)
Total: 450ms

Costs:
- Compute: All in expensive region
- Transfer: Intercontinental
- Latency: Poor user experience

Edge computing approach:

Deploy lightweight functions at edge:
- CloudFront + Lambda@Edge
- Process at 200+ edge locations
- Cache personalized content

New flow:
1. User in Asia → Tokyo edge (10ms)
2. Process at edge (20ms)
3. Response → User (10ms)
Total: 40ms

Cost comparison:
Central: $5,000/month compute + $3,000 transfer
Edge: $1,000/month functions + $500 transfer
Savings: 81% + better performance
```

### Pattern 3: The Storage Tiering Pattern

```python
# Expensive: Everything in hot storage
class DataStore:
    def store(self, key, data):
        s3.put_object(
            Bucket='hot-storage',  # $0.023/GB/month
            Key=key,
            Body=data
        )

# Optimized: Intelligent tiering
class IntelligentDataStore:
    def store(self, key, data, access_pattern='unknown'):
        if access_pattern == 'frequent':
            # Hot storage for frequently accessed
            s3.put_object(
                Bucket='hot-storage',
                Key=key,
                Body=data,
                StorageClass='STANDARD'  # $0.023/GB/month
            )
        elif access_pattern == 'infrequent':
            # Warm storage for occasional access
            s3.put_object(
                Bucket='warm-storage',
                Key=key,
                Body=data,
                StorageClass='STANDARD_IA'  # $0.0125/GB/month
            )
        else:
            # Let S3 figure it out
            s3.put_object(
                Bucket='intelligent-tiering',
                Key=key,
                Body=data,
                StorageClass='INTELLIGENT_TIERING'  # $0.0125-0.023/GB/month
            )
    
    def archive(self, key, days_old):
        if days_old > 90:
            # Move to Glacier
            s3.copy_object(
                CopySource={'Bucket': 'hot-storage', 'Key': key},
                Bucket='archive-storage',
                Key=key,
                StorageClass='GLACIER'  # $0.004/GB/month
            )

# Example savings:
# 100TB total data
# - 10TB hot (accessed daily): $230/month
# - 30TB warm (accessed weekly): $375/month  
# - 60TB cold (accessed rarely): $240/month
# Total: $845/month vs $2,300/month all hot
# Savings: 63%
```

## Successful Cost Optimizations

### 1. Netflix's Encoding Optimization

```yaml
Challenge: Video encoding costs growing exponentially

Original approach:
- Encode every video in every quality
- Store all versions
- Massive compute and storage costs

Smart encoding:
1. Analyze video complexity
2. Skip unnecessary quality levels
3. Use per-title encoding

Results:
- 50% reduction in storage
- 30% reduction in bandwidth
- Better quality at same bitrate
- Hundreds of millions in savings
```

### 2. Airbnb's Data Infrastructure

```yaml
Problem: Data warehouse costs out of control

Before:
- Multiple data copies
- Everyone queries production
- No resource limits
- Cost: $1M+/month

After:
- Tiered data access
  - Hot: Last 7 days (SSD)
  - Warm: Last 90 days (HDD)
  - Cold: Everything else (S3)
- Query routing by cost
- User quotas

Results:
- 75% cost reduction
- Faster queries (less contention)
- Better data governance
```

### 3. Spotify's Kubernetes Optimization

```yaml
Challenge: K8s clusters using 30% capacity

Solution:
1. Accurate resource requests
   - Profiled actual usage
   - Set requests to P95 usage
   - Set limits to P99 usage

2. Bin packing optimization
   - Custom scheduler
   - Considers actual usage
   - Multi-dimensional packing

3. Spot instance integration
   - Stateless workloads on spot
   - Graceful termination
   - Automatic failover

Results:
- Utilization: 30% → 75%
- Costs reduced by 60%
- No impact on reliability
```

## Cost Monitoring Implementation

### Real-time Cost Tracking

```python
class CostTracker:
    def __init__(self):
        self.meters = {}
        
    def track_operation(self, operation_type, quantity, unit_cost):
        """Track cost of an operation"""
        if operation_type not in self.meters:
            self.meters[operation_type] = {
                'count': 0,
                'total_cost': 0,
                'hourly_rate': deque(maxlen=24)
            }
        
        meter = self.meters[operation_type]
        cost = quantity * unit_cost
        
        meter['count'] += 1
        meter['total_cost'] += cost
        meter['hourly_rate'].append({
            'timestamp': datetime.now(),
            'cost': cost
        })
        
        # Alert if burn rate exceeds threshold
        hourly_burn = sum(h['cost'] for h in meter['hourly_rate'])
        if hourly_burn > COST_THRESHOLD[operation_type]:
            self.alert_high_burn_rate(operation_type, hourly_burn)
    
    def get_projection(self, operation_type, days=30):
        """Project future costs"""
        meter = self.meters.get(operation_type, {})
        if not meter:
            return 0
            
        # Calculate average hourly rate
        hourly_rate = sum(h['cost'] for h in meter['hourly_rate']) / len(meter['hourly_rate'])
        
        # Project forward
        return hourly_rate * 24 * days

# Usage
tracker = CostTracker()

# Track S3 operations
@app.route('/upload')
def upload():
    size_gb = len(request.data) / 1_073_741_824
    tracker.track_operation('s3_upload', size_gb, 0.023)  # $0.023/GB
    
# Track API calls
@app.route('/api/compute')
def compute():
    tracker.track_operation('api_compute', 1, 0.0001)  # $0.0001/request
```

## Key Insights from Cost Failures

!!! danger "Common Patterns"
    
    1. **Exponential growth surprises** - Costs can 100× overnight
    2. **Hidden multipliers compound** - Each layer adds cost
    3. **Retry logic gone wrong** - Can bankrupt you
    4. **Regional transfer costs** - Often exceed compute costs
    5. **Nobody reads the pricing page** - Until the bill arrives

## Navigation

!!! tip "Continue Learning"
    
    **Practice**: [Try Cost Optimization Exercises](exercises.md) →
    
    **Next Section**: [Part II - Foundational Pillars](../../part2-pillars/index.md) →
    
    **Tools**: [Cost Calculator](../../tools/cost-calculator.md)