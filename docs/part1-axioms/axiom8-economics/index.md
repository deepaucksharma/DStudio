# Axiom 8: Economic Gradient

<div class="axiom-header">
  <div class="learning-objective">
    <strong>Learning Objective</strong>: Every technical decision is an economic decision in disguise.
  </div>
</div>

## Core Principle

```
In distributed systems, pick two:
- Cheap + Fast = Not reliable
- Fast + Reliable = Not cheap  
- Cheap + Reliable = Not fast

Examples:
- S3: Cheap + Reliable (eventual consistency)
- DynamoDB: Fast + Reliable (expensive)
- Spot instances: Cheap + Fast (can disappear)
```

## 🎬 Failure Vignette: The Analytics Bill Shock

```
Company: Social media analytics startup
Month 1 bill: $2,000 (as expected)
Month 2 bill: $2,500 (small growth)
Month 3 bill: $28,000 (!!)

Investigation:
- New feature: Real-time sentiment analysis
- Architecture: Lambda function per tweet
- Volume: 10M tweets/day
- Lambda cost: $0.20 per 1M requests
- Kinesis cost: $0.015 per 1M records
- DynamoDB cost: $0.25 per million writes

Daily cost breakdown:
- Lambda invocations: 10M × $0.20/1M = $2
- Kinesis records: 10M × $0.015/1M = $0.15
- DynamoDB writes: 10M × $0.25/1M = $2.50
- But wait...

The hidden multiplier:
- Each tweet → 5 Lambda retries on average
- Each retry → New Kinesis record
- Each retry → New DynamoDB write
- Actual daily: $23 × 30 = $690
- Plus data transfer, CloudWatch, etc.

Root cause: Retry storm on throttling
Fix: Batch processing, reduced bill to $3,000/month
```

## Cost Dynamics in Distributed Systems

```
Linear Costs (predictable):
- Storage: $/GB/month
- Bandwidth: $/GB transferred
- Compute: $/hour

Super-linear Costs (dangerous):
- Cross-region traffic: N×(N-1) connections
- Monitoring: Every metric costs
- Coordination: Consensus overhead

Step-function Costs (surprising):
- Free tier → Paid (infinite % increase)
- Single AZ → Multi-AZ (2x)
- Regional → Global (3-5x)
```

## 🎯 Decision Tree: Serverless vs Servers

```
What's your traffic pattern?
├─ Spiky/Unpredictable
│  ├─ < 1M requests/month → Serverless
│  └─ > 1M requests/month → Check duty cycle
│     ├─ < 20% utilized → Serverless
│     └─ > 20% utilized → Servers
└─ Steady/Predictable
   ├─ Can use spot/preemptible?
   │  └─ YES → Servers with spot
   └─ Need high availability?
      └─ Servers with reserved instances
```

## The True Cost Formula

```
TCO = Infrastructure + Operations + Development + Opportunity

Where:
- Infrastructure: AWS/GCP/Azure bill
- Operations: Engineer time, on-call
- Development: Building + maintaining
- Opportunity: What you couldn't build

Example: Build vs Buy Database
Build: $50K/month infra + $200K/month engineers = $250K
Buy: $100K/month managed service
Opportunity cost of 2 engineers: 2 features/month
→ Buy wins
```

## Cost Anti-Patterns

1. **Invisible Waste**: Unused resources running 24/7
2. **Premium by Default**: Using most expensive tier
3. **Retention Forever**: Storing all data infinitely
4. **Over-provisioning**: 10x capacity "just in case"
5. **Cross-region Everything**: Replicating unnecessarily

## 🔧 Try This: Cost Attribution Tag

```python
import functools
import time
from datetime import datetime

class CostTracker:
    def __init__(self):
        self.costs = {}
    
    def track(self, resource_type, rate_per_unit):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start = time.time()
                result = func(*args, **kwargs)
                duration = time.time() - start
                
                # Calculate cost
                if resource_type == 'compute':
                    units = duration / 3600  # hours
                elif resource_type == 'api_calls':
                    units = 1  # per call
                elif resource_type == 'data_transfer':
                    units = len(str(result)) / 1e9  # GB
                
                cost = units * rate_per_unit
                
                # Track by function and day
                key = (func.__name__, datetime.now().date())
                self.costs[key] = self.costs.get(key, 0) + cost
                
                return result
            return wrapper
        return decorator
    
    def report(self):
        for (func, date), cost in sorted(self.costs.items()):
            print(f"{date} - {func}: ${cost:.4f}")

# Usage
tracker = CostTracker()

@tracker.track('compute', rate_per_unit=0.10)  # $0.10/hour
def process_data(data):
    time.sleep(0.1)  # Simulate work
    return len(data)

@tracker.track('api_calls', rate_per_unit=0.0001)  # $0.0001/call
def call_external_api():
    return "response"
```

## FinOps Quick-Win Checklist

### The 20% Effort, 80% Savings Checklist

```
□ IMMEDIATE WINS (This week)
  □ Find and terminate unused resources
    - EC2 instances with 0% CPU for 7 days
    - Unattached EBS volumes
    - Unused Elastic IPs
    - Empty S3 buckets
    Typical savings: 10-20%

  □ Right-size over-provisioned resources  
    - Instances using <20% CPU consistently
    - Over-provisioned RDS instances
    - Oversized caches
    Typical savings: 20-30%

  □ Delete old snapshots and backups
    - EBS snapshots >30 days
    - RDS snapshots (keep only required)
    - S3 lifecycle policies
    Typical savings: 5-10%

□ QUICK WINS (This month)
  □ Move to spot instances for non-critical
    - Dev/test environments
    - Batch processing
    - CI/CD runners
    Typical savings: 70-90% on those workloads

  □ Enable auto-scaling with schedules
    - Scale down nights/weekends
    - Scale up for known peaks
    Typical savings: 30-40%

  □ Compress and dedupe data
    - Enable S3 compression
    - CloudFront compression
    - Database compression
    Typical savings: 20-50% on storage/transfer

□ STRATEGIC WINS (This quarter)
  □ Reserved instances for steady workloads
    - 1-year for likely stable
    - 3-year for definitely stable
    Typical savings: 30-70%

  □ Re-architect chatty services
    - Batch API calls
    - Move to events vs polling
    - Cache repeated queries
    Typical savings: 50%+ on data transfer

  □ Region optimization
    - Move workloads to cheaper regions
    - Use regional services
    Typical savings: 10-30%
```

### Cost Optimization vs Performance Trade-offs

```
Optimization         Performance Impact    Worth it?
-----------         -----------------    ---------
Spot instances      Can be interrupted   Yes for batch
Smaller instances   Less burst capacity  Yes if sized right
Cross-AZ traffic    Added latency        No for sync calls
Cold storage        Slower retrieval     Yes for archives
Aggressive caching  Stale data risk      Yes with TTL
Single AZ           No HA                No for critical
```

## Cross-References

- → [Axiom 1: Latency](../axiom1-latency/): Time is money
- → [Axiom 5: Coordination](../axiom5-coordination/): Hidden coordination costs
- → [FinOps Patterns](../../patterns/finops): Cost optimization strategies

---

**Next**: [Synthesis: Bringing It All Together →](../synthesis/)

*"The most expensive outage is the one you didn't prevent because the prevention seemed too expensive."*