# FinOps Patterns

**When distributed systems meet the CFO**

## THE PROBLEM

```
Cloud bill shock:
- "Why is our AWS bill $500K this month?"
- "Who's running these 1000 idle instances?"
- "This query costs $100 every time!"
- "We're storing 10 copies of the same data"

Engineering efficiency ≠ Cost efficiency
```

## THE SOLUTION

```
FinOps: Engineering + Finance collaboration

VISIBILITY → OPTIMIZATION → GOVERNANCE
     ↓             ↓              ↓
 Tag & Track   Right-size    Enforce budgets
     ↓             ↓              ↓
  Dashboards   Auto-scale    Cost alerts
```

## FinOps Principles

```
1. MEASURE: You can't optimize what you can't measure
2. ALLOCATE: Every resource needs an owner
3. OPTIMIZE: Right tool for the right job
4. AUTOMATE: Machines are better at saving money
```

## IMPLEMENTATION

```python
from typing import Dict, List, Optional
import boto3
from datetime import datetime, timedelta
from collections import defaultdict

class CloudCostOptimizer:
    def __init__(self):
        self.ec2 = boto3.client('ec2')
        self.cloudwatch = boto3.client('cloudwatch')
        self.ce = boto3.client('ce')  # Cost Explorer
        
    async def analyze_instance_utilization(self):
        """Find underutilized instances"""
        
        instances = self.ec2.describe_instances()
        recommendations = []
        
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                if instance['State']['Name'] != 'running':
                    continue
                    
                # Get CPU utilization
                cpu_stats = await self.get_cpu_utilization(
                    instance['InstanceId'],
                    period_days=7
                )
                
                if cpu_stats['average'] < 10:  # Less than 10% CPU
                    recommendations.append({
                        'instance_id': instance['InstanceId'],
                        'instance_type': instance['InstanceType'],
                        'cpu_average': cpu_stats['average'],
                        'recommendation': 'TERMINATE_OR_DOWNSIZE',
                        'monthly_cost': self.estimate_instance_cost(instance),
                        'potential_savings': self.calculate_savings(instance)
                    })
                    
                elif cpu_stats['average'] < 40:  # Underutilized
                    recommendations.append({
                        'instance_id': instance['InstanceId'],
                        'current_type': instance['InstanceType'],
                        'recommended_type': self.recommend_instance_type(
                            instance, cpu_stats
                        ),
                        'potential_savings': self.calculate_downsize_savings(instance)
                    })
                    
        return recommendations
    
    async def identify_orphaned_resources(self):
        """Find resources not attached to anything"""
        
        orphans = {
            'ebs_volumes': [],
            'elastic_ips': [],
            'load_balancers': [],
            'snapshots': []
        }
        
        # Unattached EBS volumes
        volumes = self.ec2.describe_volumes(
            Filters=[{'Name': 'status', 'Values': ['available']}]
        )
        
        for volume in volumes['Volumes']:
            orphans['ebs_volumes'].append({
                'volume_id': volume['VolumeId'],
                'size_gb': volume['Size'],
                'monthly_cost': volume['Size'] * 0.10,  # $0.10/GB/month
                'age_days': (datetime.now() - volume['CreateTime']).days
            })
            
        # Unassociated Elastic IPs
        eips = self.ec2.describe_addresses()
        
        for eip in eips['Addresses']:
            if 'InstanceId' not in eip:
                orphans['elastic_ips'].append({
                    'allocation_id': eip['AllocationId'],
                    'public_ip': eip['PublicIp'],
                    'monthly_cost': 3.60  # $0.005/hour when not attached
                })
                
        return orphans

# Cost allocation and tagging
class CostAllocator:
    def __init__(self):
        self.tagging_strategy = {
            'required_tags': ['Environment', 'Team', 'Project', 'Owner'],
            'optional_tags': ['CostCenter', 'Application', 'Component']
        }
        
    async def enforce_tagging_compliance(self):
        """Ensure all resources are properly tagged"""
        
        untagged_resources = []
        
        # Check EC2 instances
        instances = self.ec2.describe_instances()
        
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                
                missing_tags = []
                for required_tag in self.tagging_strategy['required_tags']:
                    if required_tag not in tags:
                        missing_tags.append(required_tag)
                        
                if missing_tags:
                    untagged_resources.append({
                        'resource_type': 'EC2',
                        'resource_id': instance['InstanceId'],
                        'missing_tags': missing_tags,
                        'current_tags': tags
                    })
                    
        return untagged_resources
    
    async def calculate_cost_by_tag(self, tag_key: str, start_date: str, end_date: str):
        """Calculate costs grouped by tag"""
        
        response = self.ce.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {
                    'Type': 'TAG',
                    'Key': tag_key
                }
            ]
        )
        
        costs_by_tag = {}
        
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                tag_value = group['Keys'][0].replace(f'{tag_key}$', '')
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                
                if tag_value not in costs_by_tag:
                    costs_by_tag[tag_value] = 0
                costs_by_tag[tag_value] += cost
                
        return costs_by_tag

# Storage optimization
class StorageOptimizer:
    def __init__(self):
        self.s3 = boto3.client('s3')
        
    async def analyze_s3_usage(self):
        """Analyze S3 buckets for optimization"""
        
        buckets = self.s3.list_buckets()
        recommendations = []
        
        for bucket in buckets['Buckets']:
            bucket_name = bucket['Name']
            
            # Get bucket metrics
            metrics = await self.get_bucket_metrics(bucket_name)
            
            # Check for lifecycle opportunities
            if metrics['average_object_age_days'] > 30:
                recommendations.append({
                    'bucket': bucket_name,
                    'recommendation': 'ADD_LIFECYCLE_POLICY',
                    'details': {
                        'transition_to_ia': 30,  # Infrequent Access after 30 days
                        'transition_to_glacier': 90,  # Glacier after 90 days
                        'expiration': 365  # Delete after 1 year
                    },
                    'estimated_savings': self.calculate_lifecycle_savings(metrics)
                })
                
            # Check for compression opportunities
            if metrics['average_object_size'] > 1024 * 1024:  # 1MB
                recommendations.append({
                    'bucket': bucket_name,
                    'recommendation': 'ENABLE_COMPRESSION',
                    'potential_reduction': '60-80%',
                    'estimated_savings': metrics['total_size_gb'] * 0.7 * 0.023
                })
                
        return recommendations
    
    async def implement_intelligent_tiering(self, bucket_name: str):
        """Set up S3 Intelligent-Tiering"""
        
        lifecycle_config = {
            'Rules': [{
                'ID': 'IntelligentTieringRule',
                'Status': 'Enabled',
                'Transitions': [{
                    'Days': 0,
                    'StorageClass': 'INTELLIGENT_TIERING'
                }]
            }]
        }
        
        self.s3.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration=lifecycle_config
        )

# Compute optimization
class ComputeOptimizer:
    def __init__(self):
        self.spot_advisor = SpotAdvisor()
        self.savings_plans = SavingsPlansAdvisor()
        
    async def recommend_spot_instances(self, workload_type: str):
        """Recommend spot instance usage"""
        
        if workload_type in ['batch', 'processing', 'analytics']:
            return {
                'recommendation': 'USE_SPOT',
                'savings_percentage': 70,
                'implementation': {
                    'spot_fleet': True,
                    'diversification': ['t3.medium', 't3.large', 't3a.medium'],
                    'interruption_handling': 'checkpoint_and_resume'
                }
            }
        elif workload_type == 'web':
            return {
                'recommendation': 'MIXED_INSTANCES',
                'on_demand_percentage': 20,
                'spot_percentage': 80,
                'savings_percentage': 50
            }
        else:
            return {
                'recommendation': 'ON_DEMAND',
                'reason': 'Workload requires high availability'
            }
    
    async def optimize_container_costs(self):
        """Optimize container workloads"""
        
        recommendations = []
        
        # ECS optimization
        ecs_clusters = self.ecs.list_clusters()
        
        for cluster in ecs_clusters['clusterArns']:
            utilization = await self.get_cluster_utilization(cluster)
            
            if utilization['cpu'] < 50 and utilization['memory'] < 50:
                recommendations.append({
                    'cluster': cluster,
                    'recommendation': 'REDUCE_CAPACITY',
                    'current_nodes': utilization['node_count'],
                    'recommended_nodes': max(2, utilization['node_count'] // 2),
                    'monthly_savings': self.calculate_node_savings(cluster)
                })
                
        # Fargate vs EC2 analysis
        fargate_tasks = await self.analyze_fargate_usage()
        
        for task in fargate_tasks:
            if task['monthly_cost'] > 100:
                ec2_cost = self.estimate_ec2_cost(task['cpu'], task['memory'])
                
                if ec2_cost < task['monthly_cost'] * 0.7:
                    recommendations.append({
                        'task': task['name'],
                        'recommendation': 'MIGRATE_TO_EC2',
                        'current_cost': task['monthly_cost'],
                        'estimated_cost': ec2_cost,
                        'savings': task['monthly_cost'] - ec2_cost
                    })
                    
        return recommendations

# Cost anomaly detection
class CostAnomalyDetector:
    def __init__(self):
        self.historical_data = []
        self.anomaly_threshold = 1.5  # 50% increase
        
    async def detect_anomalies(self):
        """Detect unusual cost spikes"""
        
        # Get cost data for last 30 days
        costs = await self.get_daily_costs(days=30)
        
        anomalies = []
        
        for i in range(1, len(costs)):
            current = costs[i]
            previous = costs[i-1]
            
            if current['amount'] > previous['amount'] * self.anomaly_threshold:
                # Deep dive into the anomaly
                breakdown = await self.get_cost_breakdown(current['date'])
                
                anomalies.append({
                    'date': current['date'],
                    'amount': current['amount'],
                    'increase_percentage': (
                        (current['amount'] - previous['amount']) / 
                        previous['amount'] * 100
                    ),
                    'top_contributors': breakdown[:5],
                    'recommended_actions': self.recommend_actions(breakdown)
                })
                
        return anomalies
    
    def recommend_actions(self, breakdown):
        """Recommend actions based on cost breakdown"""
        
        actions = []
        
        for item in breakdown:
            if item['service'] == 'EC2' and item['usage_type'].startswith('BoxUsage'):
                actions.append({
                    'action': 'REVIEW_INSTANCE_USAGE',
                    'details': 'Check for forgotten instances or oversized instances'
                })
                
            elif item['service'] == 'DataTransfer':
                actions.append({
                    'action': 'OPTIMIZE_DATA_TRANSFER',
                    'details': 'Consider VPC endpoints, CloudFront, or data compression'
                })
                
            elif item['service'] == 'S3' and 'Requests' in item['usage_type']:
                actions.append({
                    'action': 'REDUCE_S3_REQUESTS',
                    'details': 'Batch operations, enable caching, or use CloudFront'
                })
                
        return actions

# Budget enforcement
class BudgetEnforcer:
    def __init__(self):
        self.budgets = {}
        self.actions = []
        
    def create_budget(self, name: str, amount: float, scope: dict):
        """Create budget with enforcement actions"""
        
        budget = {
            'name': name,
            'amount': amount,
            'scope': scope,  # Tags, accounts, services
            'thresholds': [
                {'percentage': 80, 'action': 'notify'},
                {'percentage': 90, 'action': 'restrict'},
                {'percentage': 100, 'action': 'terminate'}
            ]
        }
        
        self.budgets[name] = budget
        
    async def check_budgets(self):
        """Check all budgets and trigger actions"""
        
        for budget_name, budget in self.budgets.items():
            current_spend = await self.get_current_spend(budget['scope'])
            percentage = (current_spend / budget['amount']) * 100
            
            for threshold in budget['thresholds']:
                if percentage >= threshold['percentage']:
                    await self.trigger_action(
                        budget_name,
                        threshold['action'],
                        current_spend,
                        budget['amount']
                    )
                    
    async def trigger_action(self, budget_name, action, current, limit):
        """Execute budget enforcement action"""
        
        if action == 'notify':
            await self.send_notification(
                f"Budget {budget_name} at {current/limit*100:.1f}% of limit"
            )
            
        elif action == 'restrict':
            # Prevent new resource creation
            await self.apply_restrictive_policy(budget_name)
            
        elif action == 'terminate':
            # Terminate non-critical resources
            await self.terminate_non_critical_resources(budget_name)
```

## ✓ CHOOSE THIS WHEN:
• Cloud costs are significant
• Need cost visibility
• Multi-team/project environment
• Optimizing unit economics
• Regulatory compliance (cost tracking)

## ⚠️ BEWARE OF:
• Over-optimization affecting reliability
• Analysis paralysis
• Tagging compliance overhead
• Reserved capacity commitments
• Hidden costs (data transfer, requests)

## REAL EXAMPLES
• **Spotify**: 30% cost reduction via FinOps
• **Adobe**: Saved millions with automated optimization
• **Airbnb**: Cost allocation driving accountability