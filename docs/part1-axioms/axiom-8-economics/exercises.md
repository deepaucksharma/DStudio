# Economics Exercises

!!! info "Prerequisites"
    - Completed [Economics Concepts](index.md)
    - Reviewed [Economics Examples](examples.md)
    - Basic understanding of cloud pricing

!!! tip "Quick Navigation"
    [← Examples](examples.md) | 
    [↑ Axioms Overview](../index.md) |
    [→ Part II: Pillars](../../part2-pillars/index.md)

## Exercise 1: Calculate True Cost of Ownership

### Objective
Build a comprehensive cost calculator that reveals hidden expenses.

### Scenario
Your team is evaluating a new microservice architecture:
- 10 microservices
- 3 environments (dev, staging, prod)
- 2 regions for production
- Expected 1M requests/day

### Task
Create a cost calculator that includes:
1. Direct infrastructure costs
2. Operational overhead
3. Hidden multipliers
4. Human costs

### Starter Template
```python
class TrueCostCalculator:
    def __init__(self):
        # AWS pricing (simplified)
        self.pricing = {
            'ec2_t3_medium': 0.0416,  # per hour
            'alb': 0.0225,            # per hour
            'data_transfer_gb': 0.09,  # internet egress
            'cloudwatch_logs_gb': 0.50,
            'engineer_hour': 150,      # fully loaded cost
        }
    
    def calculate_infrastructure(self, services, environments, regions):
        """Calculate base infrastructure costs"""
        # Implement calculation
        pass
    
    def calculate_operational(self, services):
        """Calculate monitoring, logging, backups"""
        # Add operational overhead
        pass
    
    def calculate_human_cost(self, services):
        """Calculate engineering time required"""
        # On-call, meetings, incidents
        pass
    
    def get_total_cost(self):
        """Return comprehensive cost breakdown"""
        pass

# Usage
calc = TrueCostCalculator()
calc.add_service('api-gateway', instances=3, size='t3.medium')
calc.add_service('user-service', instances=2, size='t3.small')
# ... add more services

report = calc.get_total_cost()
print(f"Visible AWS bill: ${report['visible']}")
print(f"True total cost: ${report['total']}")
print(f"Hidden multiplier: {report['multiplier']}×")
```

### Expected Output
```
Service Breakdown:
- api-gateway: $324/month (infra) + $156/month (ops)
- user-service: $216/month (infra) + $156/month (ops)
...

Total Breakdown:
- Direct Infrastructure: $3,240/month
- Operational Overhead: $1,560/month  
- Human Cost: $12,000/month
- Total: $16,800/month
- Hidden Multiplier: 5.2×

Cost per request: $0.000016 (seems cheap!)
True cost per request: $0.000084 (reality!)
```

## Exercise 2: Optimize Data Transfer Costs

### Objective
Reduce data transfer costs in a multi-region architecture.

### Current Architecture
```yaml
Current setup:
- US-East: Primary database, application servers
- US-West: Read replica, application servers
- EU-West: Read replica, application servers

Traffic pattern:
- 100GB/day replicated to each region
- 50GB/day cross-region API calls
- 200GB/day egress to internet

Monthly costs:
- Replication: $6,000
- API calls: $3,000
- Egress: $18,000
- Total: $27,000/month
```

### Your Task
Design an optimized architecture that:
1. Maintains global presence
2. Reduces transfer costs by 50%+
3. Doesn't impact performance

### Solution Framework
```python
class DataTransferOptimizer:
    def __init__(self, current_architecture):
        self.current = current_architecture
        self.optimized = {}
        
    def analyze_traffic_patterns(self):
        """Identify optimization opportunities"""
        # Which data really needs replication?
        # Can we cache at edge?
        # Can we process locally?
        pass
        
    def implement_caching_strategy(self):
        """Add caching layers to reduce transfer"""
        # CloudFront for static content
        # Regional caches for API responses
        # Local processing where possible
        pass
        
    def optimize_replication(self):
        """Smarter replication strategy"""
        # Replicate only what's needed
        # Use compression
        # Batch transfers
        pass
        
    def calculate_savings(self):
        """Compare costs before/after"""
        pass
```

## Exercise 3: Autoscaling Cost Model

### Objective
Build a cost-aware autoscaling system that balances performance and expense.

### Requirements
- Handle 10× traffic spikes
- Maintain p99 latency < 100ms
- Minimize costs during low traffic
- Never exceed budget of $5,000/month

### Starter Code
```python
class CostAwareAutoscaler:
    def __init__(self, budget_limit):
        self.budget_limit = budget_limit
        self.current_spend = 0
        self.instance_cost_per_hour = 0.0416
        
    def calculate_required_instances(self, current_load):
        """Determine instances needed for load"""
        # Each instance handles 1000 req/s
        # Account for redundancy
        pass
        
    def get_time_based_discount(self, hour_of_day):
        """Spot prices vary by time"""
        # Implement time-based pricing
        pass
        
    def should_scale_up(self, metrics):
        """Decide if we should add instances"""
        # Consider:
        # - Current load
        # - Predicted load
        # - Budget remaining
        # - Time of day
        pass
        
    def optimize_instance_types(self, workload):
        """Choose most cost-effective instance"""
        # t3.micro: $0.0104/hour, 1000 req/s
        # t3.small: $0.0208/hour, 2500 req/s
        # t3.medium: $0.0416/hour, 5000 req/s
        # Which is most efficient?
        pass

# Test scenarios
scaler = CostAwareAutoscaler(budget_limit=5000)

# Morning spike
scaler.handle_load_change(current_rps=5000, predicted_rps=15000)

# Overnight low
scaler.handle_load_change(current_rps=500, predicted_rps=300)
```

## Exercise 4: Multi-tenant Cost Attribution

### Objective
Build a system to accurately attribute costs to tenants in a multi-tenant system.

### The Challenge
```yaml
Shared infrastructure:
- Kubernetes cluster: $10,000/month
- RDS database: $2,000/month  
- Load balancers: $500/month
- Monitoring: $1,000/month

Tenants:
- TenantA: 50% of requests, 30% of data
- TenantB: 30% of requests, 50% of data
- TenantC: 20% of requests, 20% of data

How do you fairly bill each tenant?
```

### Implementation
```python
class CostAttribution:
    def __init__(self):
        self.metrics = {}
        self.costs = {}
        
    def track_resource_usage(self, tenant_id, resource_type, amount):
        """Track what each tenant uses"""
        # CPU seconds
        # Memory GB-hours
        # Storage GB-months
        # Request count
        # Data transfer GB
        pass
        
    def calculate_base_cost_share(self):
        """Distribute fixed costs fairly"""
        # Some costs are shared (base cluster)
        # Some scale with usage
        pass
        
    def generate_bill(self, tenant_id):
        """Create itemized bill for tenant"""
        # Base platform fee
        # Usage-based charges
        # Share of fixed costs
        pass

# Example tracking
attribution = CostAttribution()

@app.route('/api/<tenant_id>/<path>')
def handle_request(tenant_id, path):
    start_time = time.time()
    
    # Track compute
    result = process_request()
    compute_time = time.time() - start_time
    attribution.track_resource_usage(
        tenant_id, 
        'compute_seconds', 
        compute_time
    )
    
    # Track data transfer
    attribution.track_resource_usage(
        tenant_id,
        'data_transfer_gb',
        len(result) / 1_073_741_824
    )
    
    return result
```

## Exercise 5: Storage Tiering Optimizer

### Objective
Implement intelligent storage tiering to minimize costs.

### Current State
```yaml
Data profile:
- Total: 1PB
- Access patterns unknown
- All in S3 Standard ($23,000/month)
- Growing 10TB/month
```

### Your Task
Build a system that:
1. Analyzes access patterns
2. Automatically moves data to appropriate tier
3. Maintains SLA for retrieval times
4. Minimizes total cost

### Implementation
```python
class StorageTieringOptimizer:
    def __init__(self):
        self.tiers = {
            'standard': {'cost_per_gb': 0.023, 'retrieval_time': '1ms'},
            'standard_ia': {'cost_per_gb': 0.0125, 'retrieval_time': '1ms'},
            'glacier_instant': {'cost_per_gb': 0.004, 'retrieval_time': '1ms'},
            'glacier_flexible': {'cost_per_gb': 0.0036, 'retrieval_time': '12hr'},
            'deep_archive': {'cost_per_gb': 0.00099, 'retrieval_time': '48hr'}
        }
        
    def analyze_access_pattern(self, object_key):
        """Determine access frequency"""
        # Track last access time
        # Count access frequency
        # Predict future access
        pass
        
    def calculate_optimal_tier(self, access_pattern, size_gb):
        """Determine most cost-effective tier"""
        # Consider access frequency
        # Consider retrieval costs
        # Consider SLA requirements
        pass
        
    def execute_tiering_plan(self, plan):
        """Move objects between tiers"""
        # Batch operations
        # Track migrations
        # Update metadata
        pass
        
    def project_savings(self, current_state, optimized_state):
        """Calculate potential savings"""
        pass

# Example usage
optimizer = StorageTieringOptimizer()

# Analyze current data
for obj in s3_inventory:
    pattern = optimizer.analyze_access_pattern(obj.key)
    optimal_tier = optimizer.calculate_optimal_tier(pattern, obj.size)
    
    if optimal_tier != obj.current_tier:
        migration_plan.add(obj, optimal_tier)

savings = optimizer.project_savings(current_state, migration_plan)
print(f"Projected monthly savings: ${savings:,.2f}")
```

## Exercise 6: Reserved Capacity Planner

### Objective
Optimize reserved instance purchases across your infrastructure.

### Current Infrastructure
```yaml
Current on-demand usage:
- 20× t3.large (constant load)
- 10× t3.large (business hours only)
- 5-30× t3.large (varies with traffic)
- Total monthly cost: $8,000

Reserved instance options:
- 1-year term: 42% discount
- 3-year term: 62% discount
- Convertible adds 10% to cost but allows changes
```

### Task
Build a planner that recommends optimal reserved capacity mix.

```python
class ReservedCapacityPlanner:
    def __init__(self, usage_history):
        self.usage_history = usage_history
        self.pricing = {
            'on_demand': 0.0832,
            'reserved_1yr': 0.0482,
            'reserved_3yr': 0.0316,
            'reserved_1yr_convertible': 0.0530,
            'reserved_3yr_convertible': 0.0348
        }
        
    def analyze_baseline_usage(self):
        """Find minimum consistent usage"""
        # What's always running?
        # Statistical analysis of usage
        pass
        
    def calculate_break_even(self, usage_pattern):
        """When do reserved instances pay off?"""
        # Account for:
        # - Usage variability
        # - Growth projections
        # - Flexibility needs
        pass
        
    def recommend_purchase_plan(self):
        """Optimal mix of reserved/on-demand"""
        # Minimize total cost
        # Maintain flexibility
        # Account for uncertainty
        pass

# Generate recommendation
planner = ReservedCapacityPlanner(historical_data)
plan = planner.recommend_purchase_plan()

print("Recommended purchase:")
print(f"3-year reserved: {plan['3yr_count']} instances")
print(f"1-year reserved: {plan['1yr_count']} instances")
print(f"Keep on-demand: {plan['on_demand_range']}")
print(f"Monthly savings: ${plan['monthly_savings']}")
print(f"Break-even: {plan['break_even_months']} months")
```

## Project: Complete Cost Optimization

### Objective
Perform a comprehensive cost optimization for a real-world-like system.

### System Profile
```yaml
Architecture:
- 15 microservices
- 3 environments
- 2 regions
- 100M requests/day
- 500TB data
- 50 engineers

Current costs:
- Infrastructure: $75,000/month
- Growing 15% monthly
- No cost visibility
```

### Deliverables
1. **Cost Attribution System**: Track costs by service, team, feature
2. **Optimization Plan**: Identify and prioritize savings opportunities
3. **Monitoring Dashboard**: Real-time cost tracking and alerts
4. **Automation Scripts**: Implement cost-saving automations
5. **ROI Analysis**: Project savings vs implementation effort

### Evaluation Criteria
- Savings potential (target 40%+)
- Implementation complexity
- Performance impact
- Risk assessment
- Payback period

## Reflection Questions

After completing exercises:

1. **Hidden Costs**: What costs surprised you the most? Why are they hidden?

2. **Trade-offs**: Where did you sacrifice functionality for cost? Was it worth it?

3. **Complexity Tax**: How does architectural complexity impact cost?

4. **Human Factor**: How much of the total cost was human time?

5. **Future Planning**: How would you design differently knowing these costs upfront?

## Navigation

!!! tip "Congratulations!"
    
    You've completed all 8 Axioms! Ready to see how they combine?
    
    **Continue to**: [Part II - Foundational Pillars](../../part2-pillars/index.md) →
    
    **Review**: [Axioms Summary](../index.md)
    
    **Tools**: [Cost Calculator](../../tools/cost-calculator.md) | [Architecture Analyzer](../../tools/architecture-analyzer.md)