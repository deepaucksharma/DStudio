---
title: "Axiom 8 Exercises: Master the Economics of Distributed Systems"
description: "Hands-on labs to calculate true costs, optimize cloud spending, and make architecture decisions based on economic reality. Learn to build systems that scale financially, not just technically."
type: axiom
difficulty: advanced
reading_time: 45 min
prerequisites: [axiom1-latency, axiom2-capacity, axiom3-failure, axiom4-concurrency, axiom5-coordination, axiom6-observability, axiom7-human, axiom8-economics]
status: complete
completion_percentage: 100
last_updated: 2025-07-21
---

<!-- Navigation -->
[Home](/) → [Part I: Axioms](/part1-axioms) → [Axiom 8](index.md) → **Economics Exercises**

# Economics Exercises

**From runaway bills to optimized architectures: master the money side of distributed systems**

---

## Hands-On Labs

### Lab 1: True Cost Calculator

**Build a system that reveals the hidden costs of distributed operations**

#### Exercise 1.1: Transaction Cost Analysis

```python
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

class AWSService(Enum):
    EC2 = "ec2"
    RDS = "rds"
    LAMBDA = "lambda"
    DYNAMODB = "dynamodb"
    S3 = "s3"
    CLOUDFRONT = "cloudfront"
    API_GATEWAY = "api_gateway"
    SQS = "sqs"
    SNS = "sns"
    ELASTICACHE = "elasticache"

@dataclass
class ServiceCost:
    """Cost components for a service"""
    compute: float = 0.0
    storage: float = 0.0
    network: float = 0.0
    requests: float = 0.0
    
    @property
    def total(self) -> float:
        return self.compute + self.storage + self.network + self.requests

class TransactionCostCalculator:
    """Calculate the true cost of distributed transactions"""
    
    def __init__(self):
# AWS Pricing (us-east-1, simplified)
        self.pricing = {
            AWSService.EC2: {
                'm5.large': 0.096 / 3600,  # per second
                'm5.xlarge': 0.192 / 3600,
                'm5.2xlarge': 0.384 / 3600
            },
            AWSService.LAMBDA: {
                'request': 0.0000002,  # per request
                'gb_second': 0.0000166667,  # per GB-second
            },
            AWSService.DYNAMODB: {
                'read_unit': 0.00013,  # per RCU
                'write_unit': 0.00065,  # per WCU  
                'storage_gb': 0.25 / 30 / 24 / 3600,  # per GB per second
            },
            AWSService.S3: {
                'put': 0.005 / 1000,  # per request
                'get': 0.0004 / 1000,  # per request
                'storage_gb': 0.023 / 30 / 24 / 3600,  # per GB per second
            },
            AWSService.API_GATEWAY: {
                'request': 0.0000035,  # per request
            },
            'network': {
                'same_az': 0.01 / 1024,  # per MB
                'cross_az': 0.02 / 1024,  # per MB
                'internet': 0.09 / 1024,  # per MB
                'cross_region': 0.02 / 1024,  # per MB
            }
        }
        
    def calculate_transaction_cost(self, transaction: Dict) -> Dict[str, float]:
        """Calculate cost breakdown for a single transaction"""
        
# TODO: Implement cost calculation that includes:
# 1. Direct service costs (compute, storage, requests)
# 2. Network transfer costs
# 3. Hidden costs (retries, timeouts, coordination)
# 4. Indirect costs (logging, monitoring, backups)
# 5. Operational costs (deployment, maintenance)
        
        costs = {}
        
# Example: E-commerce checkout transaction
# 1. API Gateway receives request
# 2. Lambda validates input
# 3. DynamoDB reads user data
# 4. Lambda calculates pricing
# 5. External payment API call
# 6. DynamoDB writes order
# 7. S3 stores receipt
# 8. SQS queues fulfillment
# 9. Lambda sends confirmation
        
        return costs
        
    def calculate_hourly_cost(self, 
                            transactions_per_hour: int,
                            transaction_profile: Dict) -> ServiceCost:
        """Calculate hourly cost for transaction volume"""
        
# TODO: Scale single transaction cost by volume
# Consider:
# - Economies of scale (reserved capacity)
# - Dis-economies of scale (higher tier pricing)
# - Peak vs average pricing
# - Burst capacity costs
        pass
        
    def optimize_architecture(self, 
                            current_costs: Dict[str, ServiceCost],
                            constraints: Dict) -> Dict:
        """Suggest architecture optimizations"""
        
# TODO: Analyze costs and suggest:
# 1. Service substitutions (Lambda -> ECS)
# 2. Caching opportunities
# 3. Data locality improvements
# 4. Batch processing opportunities
# 5. Reserved capacity recommendations
        pass

# Exercise: Calculate transaction costs
calculator = TransactionCostCalculator()

# Define a typical e-commerce transaction
checkout_transaction = {
    'name': 'checkout',
    'steps': [
        {'service': AWSService.API_GATEWAY, 'operation': 'receive_request', 'size_mb': 0.1},
        {'service': AWSService.LAMBDA, 'operation': 'validate', 'memory_mb': 512, 'duration_ms': 50},
        {'service': AWSService.DYNAMODB, 'operation': 'read', 'rcu': 2, 'items': 3},
        {'service': AWSService.LAMBDA, 'operation': 'calculate', 'memory_mb': 1024, 'duration_ms': 200},
        {'service': 'external', 'operation': 'payment_api', 'latency_ms': 500},
        {'service': AWSService.DYNAMODB, 'operation': 'write', 'wcu': 5, 'items': 2},
        {'service': AWSService.S3, 'operation': 'put', 'size_mb': 0.5},
        {'service': AWSService.SQS, 'operation': 'send', 'messages': 1},
        {'service': AWSService.LAMBDA, 'operation': 'notify', 'memory_mb': 256, 'duration_ms': 100}
    ]
}

# Calculate costs
transaction_cost = calculator.calculate_transaction_cost(checkout_transaction)
print(f"Cost per transaction: ${sum(transaction_cost.values()):.6f}")

# Scale to daily volume
daily_transactions = 1_000_000
daily_cost = sum(transaction_cost.values()) * daily_transactions
print(f"Daily cost at {daily_transactions:,} transactions: ${daily_cost:,.2f}")
print(f"Annual cost: ${daily_cost * 365:,.2f}")
```

#### Exercise 1.2: Hidden Cost Detector

```python
class HiddenCostDetector:
    """Find costs that don't show up in simple calculations"""
    
    def __init__(self):
        self.cost_patterns = {
            'retry_storms': {
                'description': 'Exponential retries causing cost explosion',
                'multiplier': lambda retry_rate: math.pow(2, retry_rate * 10),
                'example': 'DynamoDB throttling causing Lambda retries'
            },
            'data_transfer': {
                'description': 'Cross-AZ/region data transfer',
                'multiplier': lambda gb_transferred: gb_transferred * 0.02,
                'example': 'Database replica in different AZ'
            },
            'idle_resources': {
                'description': 'Paying for unused capacity',
                'multiplier': lambda utilization: 1.0 / max(utilization, 0.01),
                'example': 'EC2 instances at 10% CPU'
            },
            'overprovisioning': {
                'description': 'Resources sized for peak, used at average',
                'multiplier': lambda peak_to_avg_ratio: peak_to_avg_ratio,
                'example': 'RDS sized for Black Friday, idle in January'
            },
            'monitoring_overhead': {
                'description': 'Cost of observability',
                'multiplier': lambda detail_level: 1 + (detail_level * 0.3),
                'example': 'Detailed CloudWatch metrics and logs'
            }
        }
        
    def analyze_architecture(self, architecture: Dict) -> List[Dict]:
        """Find hidden costs in architecture"""
        
        hidden_costs = []
        
# TODO: Implement detection for:
# 1. Retry amplification
# 2. Unnecessary data movement
# 3. Inefficient caching
# 4. Suboptimal service choices
# 5. Missing autoscaling
# 6. Expensive consistency guarantees
        
        return hidden_costs
        
    def calculate_true_cost(self, visible_cost: float, 
                          architecture: Dict) -> Dict[str, float]:
        """Calculate true cost including hidden factors"""
        
        hidden_costs = self.analyze_architecture(architecture)
        
        true_cost_breakdown = {
            'visible': visible_cost,
            'hidden': sum(hc['cost'] for hc in hidden_costs),
            'operational': self.estimate_operational_cost(architecture),
            'opportunity': self.calculate_opportunity_cost(architecture)
        }
        
        true_cost_breakdown['total'] = sum(true_cost_breakdown.values())
        
        return true_cost_breakdown
        
    def generate_optimization_report(self, hidden_costs: List[Dict]) -> str:
        """Generate actionable optimization report"""
        
# TODO: Create report with:
# 1. Ranked list of cost savings
# 2. Implementation difficulty
# 3. Risk assessment
# 4. Step-by-step fixes
# 5. Expected ROI
        pass

# Exercise: Find hidden costs
detector = HiddenCostDetector()

# Example architecture
architecture = {
    'services': {
        'api': {'type': 'ec2', 'instances': 20, 'utilization': 0.3},
        'database': {'type': 'rds', 'size': 'db.r5.4xlarge', 'multi_az': True},
        'cache': {'type': 'elasticache', 'nodes': 3, 'hit_rate': 0.4},
        'storage': {'type': 's3', 'data_gb': 5000, 'requests_per_day': 10_000_000}
    },
    'patterns': {
        'retry_rate': 0.15,  # 15% of requests retry
        'peak_to_average': 4.5,  # 4.5x traffic at peak
        'cross_az_traffic_gb': 1000  # Daily
    }
}

hidden_costs = detector.analyze_architecture(architecture)
print("Hidden costs found:")
for cost in hidden_costs:
    print(f"- {cost['type']}: ${cost['monthly_cost']:,.2f}")
    print(f"  Cause: {cost['description']}")
    print(f"  Fix: {cost['recommendation']}")
```

---

### Lab 2: Cloud Cost Optimization Workshop

**Learn to cut cloud costs without cutting corners**

#### Exercise 2.1: Multi-Cloud Cost Optimizer

```python
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import pandas as pd

class MultiCloudOptimizer:
    """Optimize costs across AWS, GCP, and Azure"""
    
    def __init__(self):
# Simplified pricing for comparison
        self.cloud_pricing = {
            'aws': {
                'compute': {
                    't3.medium': 0.0416,
                    't3.large': 0.0832,
                    't3.xlarge': 0.1664,
                    'm5.large': 0.096,
                    'm5.xlarge': 0.192
                },
                'storage': {
                    'ssd': 0.10,  # per GB/month
                    'hdd': 0.045
                },
                'network': {
                    'ingress': 0,
                    'egress': 0.09,  # per GB
                    'cross_region': 0.02
                }
            },
            'gcp': {
                'compute': {
                    'e2-medium': 0.0334,
                    'e2-standard-2': 0.0670,
                    'e2-standard-4': 0.1340,
                    'n2-standard-2': 0.0971,
                    'n2-standard-4': 0.1942
                },
                'storage': {
                    'ssd': 0.17,
                    'hdd': 0.04
                },
                'network': {
                    'ingress': 0,
                    'egress': 0.12,  # per GB (tiered)
                    'cross_region': 0.01
                }
            },
            'azure': {
                'compute': {
                    'B2s': 0.0416,
                    'B2ms': 0.0832,
                    'D2s_v3': 0.096,
                    'D4s_v3': 0.192
                },
                'storage': {
                    'ssd': 0.135,
                    'hdd': 0.05
                },
                'network': {
                    'ingress': 0,
                    'egress': 0.087,
                    'cross_region': 0.02
                }
            }
        }
        
    def analyze_workload(self, workload: Dict) -> Dict[str, float]:
        """Analyze workload costs across clouds"""
        
# TODO: Calculate total cost for workload on each cloud
# Consider:
# 1. Compute costs (including sustained use discounts)
# 2. Storage costs (including snapshots, backups)
# 3. Network costs (including CDN)
# 4. Service-specific costs
# 5. Support costs
        pass
        
    def optimize_placement(self, workloads: List[Dict], 
                         constraints: Dict) -> Dict:
        """Optimize workload placement across clouds"""
        
# TODO: Implement multi-cloud optimization
# Constraints might include:
# - Data residency requirements
# - Service availability
# - Egress costs
# - Existing commitments
# - Migration costs
        pass
        
    def calculate_migration_roi(self, 
                              current_state: Dict,
                              target_state: Dict) -> Dict:
        """Calculate ROI of migration"""
        
        migration_costs = {
            'data_transfer': self.calculate_transfer_cost(current_state, target_state),
            'dual_running': self.calculate_dual_run_cost(current_state),
            'engineering': self.estimate_engineering_cost(current_state, target_state),
            'downtime': self.estimate_downtime_cost(current_state)
        }
        
        monthly_savings = (current_state['monthly_cost'] - 
                         target_state['monthly_cost'])
        
        payback_months = sum(migration_costs.values()) / max(monthly_savings, 1)
        
        return {
            'migration_cost': sum(migration_costs.values()),
            'monthly_savings': monthly_savings,
            'payback_months': payback_months,
            'three_year_roi': (monthly_savings * 36 - sum(migration_costs.values())),
            'recommendation': 'migrate' if payback_months < 12 else 'stay'
        }

# Exercise: Multi-cloud optimization
optimizer = MultiCloudOptimizer()

# Define workloads
workloads = [
    {
        'name': 'web_frontend',
        'compute': {'instances': 10, 'type': 'medium', 'hours': 24*30},
        'storage': {'ssd_gb': 100, 'hdd_gb': 1000},
        'network': {'egress_gb': 5000, 'cross_region_gb': 100},
        'constraints': ['low_latency']
    },
    {
        'name': 'data_processing',
        'compute': {'instances': 50, 'type': 'xlarge', 'hours': 8*20},  # 8hrs, 20 days
        'storage': {'ssd_gb': 500, 'hdd_gb': 50000},
        'network': {'egress_gb': 100, 'cross_region_gb': 1000},
        'constraints': ['gpu_required']
    },
    {
        'name': 'development',
        'compute': {'instances': 5, 'type': 'large', 'hours': 8*20},
        'storage': {'ssd_gb': 50, 'hdd_gb': 200},
        'network': {'egress_gb': 10, 'cross_region_gb': 0},
        'constraints': ['none']
    }
]

# Analyze each workload
for workload in workloads:
    costs = optimizer.analyze_workload(workload)
    print(f"\nWorkload: {workload['name']}")
    print(f"AWS: ${costs.get('aws', 0):,.2f}/month")
    print(f"GCP: ${costs.get('gcp', 0):,.2f}/month")
    print(f"Azure: ${costs.get('azure', 0):,.2f}/month")
    print(f"Optimal: {min(costs.items(), key=lambda x: x[1])[0]}")
```

#### Exercise 2.2: FinOps Automation Platform

```python
class FinOpsPlatform:
    """Automated FinOps for continuous optimization"""
    
    def __init__(self):
        self.cost_history = []
        self.optimization_rules = []
        self.alerts = []
        
    def add_optimization_rule(self, 
                            name: str,
                            condition: str,
                            action: str,
                            expected_savings: float):
        """Add automated optimization rule"""
        
        rule = {
            'name': name,
            'condition': condition,
            'action': action,
            'expected_savings': expected_savings,
            'enabled': True,
            'executions': 0,
            'actual_savings': 0
        }
        
        self.optimization_rules.append(rule)
        
    def scan_for_optimizations(self, 
                              cloud_accounts: List[Dict]) -> List[Dict]:
        """Scan all accounts for optimization opportunities"""
        
        opportunities = []
        
# TODO: Implement scanners for:
# 1. Unused resources (EC2, EBS, EIPs)
# 2. Oversized instances
# 3. Old snapshots and AMIs
# 4. Unattached volumes
# 5. Idle load balancers
# 6. Non-optimized S3 storage classes
# 7. Missing reserved instances
# 8. Inefficient auto-scaling
        
# Example scanner
        for account in cloud_accounts:
# Check for idle instances
            idle_instances = self.find_idle_instances(account)
            for instance in idle_instances:
                opportunities.append({
                    'type': 'idle_instance',
                    'resource': instance['id'],
                    'current_cost': instance['monthly_cost'],
                    'action': 'terminate_or_stop',
                    'savings': instance['monthly_cost'],
                    'confidence': 0.95
                })
                
        return opportunities
        
    def execute_optimization(self, optimization: Dict) -> Dict:
        """Execute an optimization with safety checks"""
        
# TODO: Implement safe execution:
# 1. Validate optimization still valid
# 2. Take backup/snapshot if needed
# 3. Execute change
# 4. Verify no service impact
# 5. Track actual savings
# 6. Rollback if needed
        pass
        
    def generate_executive_report(self) -> str:
        """Generate executive-friendly cost report"""
        
        report = f"""
# Cloud Cost Optimization Report
## Executive Summary

### Current State
- Monthly Spend: ${self.get_current_spend():,.2f}
- YoY Growth: {self.get_yoy_growth():.1%}
- Cost per Transaction: ${self.get_cost_per_transaction():.4f}

### Optimization Results
- Identified Savings: ${self.get_identified_savings():,.2f}/month
- Implemented Savings: ${self.get_implemented_savings():,.2f}/month
- Success Rate: {self.get_success_rate():.1%}

### Top Opportunities
{self.format_top_opportunities()}

### Recommendations
1. {self.get_top_recommendation()}
2. {self.get_second_recommendation()}
3. {self.get_third_recommendation()}

### Risk Assessment
- No impact on reliability: ✅
- Rollback plan tested: ✅
- Stakeholder approval: ✅
        """
        
        return report

# Exercise: Build FinOps automation
finops = FinOpsPlatform()

# Add optimization rules
finops.add_optimization_rule(
    "terminate_idle_dev",
    "instance.environment == 'dev' AND cpu_avg < 5% for 7 days",
    "terminate_instance",
    expected_savings=500
)

finops.add_optimization_rule(
    "rightsize_oversized",
    "cpu_p99 < 40% AND memory_p99 < 50% for 30 days",
    "downsize_instance",
    expected_savings=1000
)

finops.add_optimization_rule(
    "s3_lifecycle",
    "s3_object.age > 90 days AND access_count == 0",
    "move_to_glacier",
    expected_savings=2000
)

# Scan for optimizations
cloud_accounts = [
    {'id': 'prod-account', 'provider': 'aws', 'monthly_spend': 50000},
    {'id': 'dev-account', 'provider': 'aws', 'monthly_spend': 10000},
    {'id': 'data-account', 'provider': 'gcp', 'monthly_spend': 30000}
]

opportunities = finops.scan_for_optimizations(cloud_accounts)
print(f"Found {len(opportunities)} optimization opportunities")
print(f"Total potential savings: ${sum(o['savings'] for o in opportunities):,.2f}/month")
```

---

### Lab 3: Cost-Aware Architecture Design

**Design systems with cost as a first-class constraint**

#### Exercise 3.1: Serverless vs Containers Calculator

```python
class ServerlessVsContainerCalculator:
    """Determine optimal compute strategy based on usage patterns"""
    
    def __init__(self):
# Pricing models
        self.serverless_pricing = {
            'lambda': {
                'request': 0.0000002,
                'gb_second': 0.0000166667,
                'free_tier_requests': 1_000_000,
                'free_tier_gb_seconds': 400_000
            },
            'api_gateway': {
                'request': 0.0000035,
                'cache_gb_hour': 0.02
            }
        }
        
        self.container_pricing = {
            'fargate': {
                'vcpu_hour': 0.04048,
                'gb_hour': 0.004445
            },
            'ecs_ec2': {
                'm5.large': 0.096,
                'm5.xlarge': 0.192,
                'm5.2xlarge': 0.384
            },
            'eks': {
                'cluster_hour': 0.10,
                'node_hour': {  # Plus EC2 costs
                    'm5.large': 0.096,
                    'm5.xlarge': 0.192
                }
            }
        }
        
    def calculate_serverless_cost(self,
                                requests_per_month: int,
                                avg_duration_ms: float,
                                avg_memory_mb: float) -> Dict[str, float]:
        """Calculate monthly cost for serverless"""
        
# TODO: Calculate considering:
# 1. Free tier
# 2. Cold start overhead
# 3. API Gateway costs
# 4. Additional services (DynamoDB, S3)
# 5. Monitoring costs
        pass
        
    def calculate_container_cost(self,
                               requests_per_month: int,
                               avg_duration_ms: float,
                               container_memory_mb: float,
                               container_cpu: float) -> Dict[str, float]:
        """Calculate monthly cost for containers"""
        
# TODO: Calculate considering:
# 1. Always-on costs
# 2. Auto-scaling efficiency
# 3. Load balancer costs
# 4. Container registry
# 5. Orchestration overhead
        pass
        
    def find_break_even_point(self,
                            memory_mb: float,
                            duration_ms: float) -> int:
        """Find requests/month where costs are equal"""
        
# TODO: Binary search to find break-even
# Return requests per month where serverless = containers
        pass
        
    def generate_recommendation(self,
                              usage_pattern: Dict) -> Dict:
        """Recommend compute strategy based on usage"""
        
# TODO: Consider:
# 1. Request patterns (steady vs spiky)
# 2. Predictability
# 3. Scaling requirements
# 4. Cold start tolerance
# 5. Complexity requirements
        pass

# Exercise: Find optimal compute strategy
calculator = ServerlessVsContainerCalculator()

# Test different usage patterns
usage_patterns = [
    {
        'name': 'API Backend',
        'requests_per_month': 10_000_000,
        'avg_duration_ms': 100,
        'memory_mb': 512,
        'pattern': 'steady',
        'peak_to_average': 2
    },
    {
        'name': 'Batch Processing',
        'requests_per_month': 100_000,
        'avg_duration_ms': 30_000,  # 30 seconds
        'memory_mb': 3008,
        'pattern': 'scheduled',
        'peak_to_average': 1
    },
    {
        'name': 'Event Processing',
        'requests_per_month': 1_000_000,
        'avg_duration_ms': 500,
        'memory_mb': 1024,
        'pattern': 'bursty',
        'peak_to_average': 10
    }
]

for pattern in usage_patterns:
    serverless_cost = calculator.calculate_serverless_cost(
        pattern['requests_per_month'],
        pattern['avg_duration_ms'],
        pattern['memory_mb']
    )
    
    container_cost = calculator.calculate_container_cost(
        pattern['requests_per_month'],
        pattern['avg_duration_ms'],
        pattern['memory_mb'],
        0.5  # CPU units
    )
    
    print(f"\n{pattern['name']}:")
    print(f"Serverless: ${serverless_cost['total']:,.2f}/month")
    print(f"Containers: ${container_cost['total']:,.2f}/month")
    print(f"Recommendation: {'Serverless' if serverless_cost['total'] < container_cost['total'] else 'Containers'}")
    
    break_even = calculator.find_break_even_point(
        pattern['memory_mb'],
        pattern['avg_duration_ms']
    )
    print(f"Break-even: {break_even:,} requests/month")
```

#### Exercise 3.2: Cost-Aware Auto-scaling

```python
class CostAwareAutoScaler:
    """Auto-scaling that considers cost, not just performance"""
    
    def __init__(self):
        self.scaling_history = []
        self.cost_targets = {}
        self.performance_slos = {}
        
    def calculate_optimal_capacity(self,
                                 current_load: float,
                                 cost_budget: float,
                                 slo_target: float) -> int:
        """Calculate optimal instance count"""
        
# TODO: Implement optimization that balances:
# 1. Meeting SLO targets
# 2. Staying within budget
# 3. Handling predicted load
# 4. Minimizing waste
# 5. Smooth scaling (avoid thrashing)
        pass
        
    def predict_cost_impact(self,
                          scaling_decision: Dict) -> Dict[str, float]:
        """Predict cost impact of scaling decision"""
        
        costs = {
            'immediate': self.calculate_immediate_cost(scaling_decision),
            'hourly': self.calculate_hourly_cost(scaling_decision),
            'daily': self.calculate_daily_cost(scaling_decision),
            'if_traffic_continues': self.project_cost(scaling_decision)
        }
        
        return costs
        
    def implement_spot_strategy(self,
                              workload_type: str,
                              interruption_tolerance: float) -> Dict:
        """Design spot instance strategy"""
        
# TODO: Implement strategy considering:
# 1. Interruption rate by instance type
# 2. Price volatility
# 3. Diversification across types/AZs
# 4. Fallback to on-demand
# 5. State checkpointing
        pass

# Exercise: Cost-aware scaling
scaler = CostAwareAutoScaler()

# Define workload
workload = {
    'current_load': 75.0,  # percentage
    'trend': 'increasing',
    'rate_of_change': 5.0,  # percent per hour
    'instance_type': 'm5.large',
    'current_instances': 10,
    'min_instances': 2,
    'max_instances': 100
}

# Define constraints
constraints = {
    'budget_per_hour': 50.0,  # dollars
    'response_time_p99_ms': 100,
    'error_rate_threshold': 0.001
}

# Calculate optimal scaling
optimal = scaler.calculate_optimal_capacity(
    workload['current_load'],
    constraints['budget_per_hour'],
    constraints['response_time_p99_ms']
)

print(f"Current instances: {workload['current_instances']}")
print(f"Optimal instances: {optimal}")
print(f"Cost impact: ${scaler.predict_cost_impact({'target': optimal})['hourly']:.2f}/hour")
```

---

### Lab 4: Economic Architecture Patterns

**Learn patterns that save millions**

#### Exercise 4.1: Data Locality Optimizer

```python
class DataLocalityOptimizer:
    """Optimize data placement to minimize transfer costs"""
    
    def __init__(self):
        self.regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
        self.transfer_costs = {
            'within_az': 0,
            'cross_az': 0.01,  # per GB
            'cross_region': 0.02,  # per GB
            'internet': 0.09  # per GB
        }
        
    def analyze_data_flows(self, 
                         services: List[Dict],
                         data_flows: List[Dict]) -> Dict:
        """Analyze current data transfer costs"""
        
# TODO: Build graph of data flows
# Calculate monthly transfer costs
# Identify expensive paths
        pass
        
    def optimize_placement(self,
                         services: List[Dict],
                         constraints: Dict) -> Dict:
        """Optimize service placement for minimal transfer costs"""
        
# TODO: Implement optimization considering:
# 1. Data gravity (where is most data?)
# 2. User proximity requirements
# 3. Compliance constraints
# 4. Service dependencies
# 5. Migration costs
        pass
        
    def calculate_savings(self,
                        current_placement: Dict,
                        optimal_placement: Dict) -> float:
        """Calculate monthly savings from optimization"""
        
# TODO: Compare transfer costs
        pass

# Exercise: Optimize data locality
optimizer = DataLocalityOptimizer()

# Current architecture
current_services = [
    {'name': 'web_app', 'region': 'us-east-1', 'data_out_gb': 1000},
    {'name': 'api', 'region': 'us-east-1', 'data_out_gb': 5000},
    {'name': 'database', 'region': 'us-west-2', 'data_out_gb': 2000},
    {'name': 'analytics', 'region': 'eu-west-1', 'data_out_gb': 10000},
    {'name': 'cdn', 'region': 'global', 'data_out_gb': 50000}
]

data_flows = [
    {'from': 'web_app', 'to': 'api', 'gb_per_month': 500},
    {'from': 'api', 'to': 'database', 'gb_per_month': 2000},
    {'from': 'database', 'to': 'analytics', 'gb_per_month': 5000},
    {'from': 'api', 'to': 'cdn', 'gb_per_month': 10000}
]

# Analyze current costs
current_costs = optimizer.analyze_data_flows(current_services, data_flows)
print(f"Current monthly transfer costs: ${current_costs['total']:,.2f}")

# Find optimal placement
optimal = optimizer.optimize_placement(
    current_services,
    constraints={'compliance': 'eu_data_in_eu'}
)
print(f"\nOptimal placement:")
for service, region in optimal['placement'].items():
    print(f"  {service}: {region}")
print(f"\nExpected savings: ${optimal['monthly_savings']:,.2f}")
```

#### Exercise 4.2: Reserved Capacity Optimizer

```python
class ReservedCapacityOptimizer:
    """Optimize reserved instance purchases"""
    
    def __init__(self):
        self.reservation_types = {
            'ec2_standard_1yr': {'discount': 0.40, 'upfront': 0.5},
            'ec2_standard_3yr': {'discount': 0.60, 'upfront': 0.5},
            'ec2_convertible_1yr': {'discount': 0.31, 'upfront': 0.5},
            'ec2_convertible_3yr': {'discount': 0.45, 'upfront': 0.5},
            'rds_1yr': {'discount': 0.30, 'upfront': 0},
            'rds_3yr': {'discount': 0.50, 'upfront': 0}
        }
        
    def analyze_usage_patterns(self,
                             historical_usage: pd.DataFrame) -> Dict:
        """Analyze usage to find reservation opportunities"""
        
# TODO: Analyze usage patterns to find:
# 1. Baseline usage (always on)
# 2. Predictable patterns
# 3. Growth trends
# 4. Seasonal variations
        pass
        
    def optimize_reservations(self,
                            usage_analysis: Dict,
                            cash_constraints: Dict) -> Dict:
        """Optimize reservation purchases"""
        
# TODO: Implement optimization considering:
# 1. Cash flow constraints
# 2. Risk tolerance
# 3. Expected growth
# 4. Flexibility needs
# 5. Break-even analysis
        pass
        
    def calculate_commitment_impact(self,
                                  reservation_plan: Dict) -> Dict:
        """Calculate financial impact of reservations"""
        
# TODO: Calculate:
# 1. Upfront payment required
# 2. Monthly savings
# 3. Break-even point
# 4. Risk if usage decreases
# 5. Total 3-year savings
        pass

# Exercise: Optimize reserved capacity
optimizer = ReservedCapacityOptimizer()

# Load historical usage (mock data)
import numpy as np
dates = pd.date_range('2024-01-01', periods=365, freq='D')
usage_data = pd.DataFrame({
    'date': dates,
    'm5.large': np.random.poisson(50, 365) + np.sin(np.arange(365) * 2 * np.pi / 365) * 10,
    'm5.xlarge': np.random.poisson(20, 365),
    'db.r5.large': np.ones(365) * 5,  # Steady database usage
    'db.r5.xlarge': np.ones(365) * 2
})

# Analyze patterns
patterns = optimizer.analyze_usage_patterns(usage_data)
print("Usage patterns detected:")
for instance_type, pattern in patterns.items():
    print(f"  {instance_type}: baseline={pattern['baseline']:.1f}, peak={pattern['peak']:.1f}")

# Optimize reservations
cash_constraints = {
    'max_upfront': 100000,
    'monthly_budget': 50000,
    'risk_tolerance': 'medium'
}

reservation_plan = optimizer.optimize_reservations(patterns, cash_constraints)
print(f"\nRecommended reservations:")
for reservation in reservation_plan['recommendations']:
    print(f"  {reservation['type']}: {reservation['count']} x {reservation['term']}")
    print(f"    Upfront: ${reservation['upfront']:,.2f}")
    print(f"    Monthly savings: ${reservation['monthly_savings']:,.2f}")
```

---

## 💪 Challenge Problems

### Challenge 1: The Multi-Region Optimizer

```python
"""
Scenario: Design a system that serves users globally with:
- 100ms latency SLO
- 99.99% availability  
- $100K/month budget
- 50M daily active users
- 1TB new data daily

Optimize for:
1. Minimal cost while meeting SLOs
2. Data transfer costs
3. Compliance (data residency)
4. Disaster recovery
5. Elasticity for traffic spikes

Provide:
- Architecture diagram
- Cost breakdown by region
- Data flow optimization
- Failure scenarios handled
- Scaling strategy
"""

class GlobalSystemOptimizer:
# Your implementation here
    pass
```

### Challenge 2: The Penny-Pinching Startup

```python
"""
You have $1,000/month to build:
- API serving 1M requests/day
- Database with 100GB data
- Analytics on all events
- Mobile app backend
- Admin dashboard
- Monitoring/alerting
- CI/CD pipeline
- Dev/staging environments

Design a system that:
1. Stays under budget
2. Can scale 10x without rearchitecture
3. Maintains 99.9% uptime
4. Provides good developer experience

Show month-by-month growth plan from $1K to $10K budget.
"""

class StartupArchitecture:
# Your implementation here
    pass
```

### Challenge 3: The Cost Attribution System

```python
"""
Build a system that accurately attributes costs to:
- Individual customers
- Feature teams  
- Product lines
- API endpoints
- Specific transactions

Requirements:
- Real-time cost visibility
- Historical analysis
- Forecasting
- Anomaly detection
- Chargeback/showback

Handle:
- Shared resources
- Indirect costs
- Peak vs average usage
- Reserved capacity allocation
- Support/operational costs
"""

class CostAttributionSystem:
# Your implementation here
    pass
```

---

## Research Projects

### Project 1: Predictive Cost Optimization

```python
class PredictiveCostOptimizer:
    """ML-based cost prediction and optimization"""
    
    def __init__(self):
        self.models = {}
        self.optimization_history = []
        
    def train_cost_predictor(self, 
                           historical_data: pd.DataFrame):
        """Train model to predict future costs"""
# TODO: Implement using:
# - Time series analysis
# - Seasonality detection
# - Growth trend modeling
# - External factor correlation
        pass
        
    def predict_cost_anomalies(self,
                             real_time_metrics: Dict) -> List[Dict]:
        """Predict cost spikes before they happen"""
# TODO: Real-time anomaly detection
        pass
        
    def recommend_preventive_actions(self,
                                   predicted_anomaly: Dict) -> List[Dict]:
        """Suggest actions to prevent cost spikes"""
# TODO: Generate actionable recommendations
        pass

# Research: Build and validate predictor
```

### Project 2: Economic Modeling of Distributed Systems

```python
"""
Research Project: Create economic models for:

1. Cost of consistency levels
2. Price of availability (each 9)
3. Latency-cost tradeoffs
4. Value of caching
5. Economics of data replication

Deliver:
- Mathematical models
- Validation against real systems
- Decision frameworks
- Cost calculators
- Optimization algorithms
"""

class DistributedSystemsEconomics:
# Your research here
    pass
```

---

## 📑 Quick Reference: Cost Optimization Checklist

```python
cost_optimization_checklist = {
    'immediate_wins': [
        'Delete unattached EBS volumes',
        'Release unassociated Elastic IPs',
        'Clean up old snapshots',
        'Remove unused load balancers',
        'Terminate stopped instances > 30 days',
        'Delete old AMIs',
        'Clean S3 incomplete multipart uploads'
    ],
    'quick_wins': [
        'Enable S3 lifecycle policies',
        'Right-size EC2 instances',
        'Use Spot for dev/test',
        'Enable Auto Scaling',
        'Compress CloudWatch logs',
        'Reduce log retention',
        'Optimize data transfer paths'
    ],
    'strategic_wins': [
        'Refactor to serverless',
        'Implement caching layers',
        'Optimize database queries',
        'Use reserved instances',
        'Negotiate enterprise discounts',
        'Multi-cloud arbitrage',
        'Re-architect for cost'
    ]
}

def calculate_potential_savings(account_data: Dict) -> float:
    """Estimate savings from optimization checklist"""
# Typical savings percentages
    savings_potential = {
        'immediate_wins': 0.05,  # 5% of bill
        'quick_wins': 0.15,      # 15% of bill  
        'strategic_wins': 0.30   # 30% of bill
    }
    
    total_savings = 0
    for category, percentage in savings_potential.items():
        total_savings += account_data['monthly_spend'] * percentage
        
    return total_savings
```

---

## Skills Assessment

Rate your understanding (1-5):
- [ ] Can calculate true transaction costs
- [ ] Understand cloud pricing models
- [ ] Can optimize multi-cloud deployments
- [ ] Know when serverless beats containers
- [ ] Can design cost-aware architectures
- [ ] Understand FinOps practices
- [ ] Can implement cost attribution
- [ ] Can predict and prevent cost spikes

**Score: ___/40** (32+ = Expert, 24-32 = Proficient, 16-24 = Intermediate, <16 = Keep practicing!)

---

## Final Challenge: The Unicorn Optimizer

```python
"""
The Ultimate Test: You're the first engineer at a unicorn startup.

Starting point:
- $10K/month budget
- 1K users
- Basic MVP

End goal (3 years):
- $10M/month budget
- 100M users  
- Global presence
- Multiple products
- 99.99% availability

Design the complete cost evolution strategy:
1. Architecture at each growth stage
2. When to migrate/refactor
3. Build vs buy decisions
4. Team scaling vs automation
5. Cost per user targets

Show how to grow 1000x while keeping costs linear (not exponential).
"""

class UnicornCostStrategy:
# Your implementation here
    pass
```

---

**Previous**: [Examples](examples.md) | **Next**: [Part I Summary](/part1-axioms/archive-old-8-axiom-structure/summary)

**Related**: [Capacity Planning](/quantitative/capacity-planning) • [Auto-scaling](/patterns/auto-scaling) • [Multi-region](/patterns/multi-region)
