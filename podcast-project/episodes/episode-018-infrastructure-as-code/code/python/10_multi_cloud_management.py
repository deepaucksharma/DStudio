#!/usr/bin/env python3
"""
Multi-Cloud Infrastructure Management System
Episode 18: Infrastructure as Code

Comprehensive multi-cloud management for Indian enterprises।
AWS, Azure, and GCP unified management के साथ cost optimization।

Cost Estimate: ₹30,000-80,000 per month for multi-cloud setup
"""

import os
import json
import yaml
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import boto3
import requests
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from google.cloud import compute_v1
import asyncio
import concurrent.futures
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CloudProvider(Enum):
    """Cloud provider enumeration"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"

@dataclass
class CloudResource:
    """Generic cloud resource representation"""
    provider: CloudProvider
    resource_type: str
    resource_id: str
    name: str
    region: str
    status: str
    cost_per_hour: float
    tags: Dict[str, str]
    metadata: Dict[str, Any] = None
    
    def to_dict(self):
        return asdict(self)

@dataclass
class CostSummary:
    """Cost summary for cloud resources"""
    provider: CloudProvider
    daily_cost: float
    monthly_cost: float
    yearly_cost: float
    currency: str = "INR"
    resources_count: int = 0
    top_expensive_resources: List[str] = None

class MultiCloudManager:
    """Multi-cloud infrastructure management system"""
    
    def __init__(self, config_file: str = "multi-cloud-config.yml"):
        self.config = self.load_config(config_file)
        self.resources = {}
        
        # Initialize cloud clients
        self.aws_clients = {}
        self.azure_clients = {}
        self.gcp_clients = {}
        
        self.setup_cloud_clients()
        
        logger.info("Multi-Cloud Manager initialized")
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load multi-cloud configuration"""
        
        default_config = {
            'aws': {
                'regions': ['ap-south-1', 'ap-southeast-1'],  # Mumbai, Singapore
                'profile': 'default',
                'services': ['ec2', 'rds', 'elasticache', 'elbv2', 's3']
            },
            'azure': {
                'regions': ['centralindia', 'southeastasia'],  # Central India, Southeast Asia
                'subscription_id': 'your-subscription-id',
                'services': ['compute', 'storage', 'database', 'network']
            },
            'gcp': {
                'regions': ['asia-south1', 'asia-southeast1'],  # Mumbai, Singapore
                'project_id': 'your-project-id',
                'services': ['compute', 'sql', 'storage', 'kubernetes']
            },
            'cost_thresholds': {
                'daily_alert': 5000,  # INR
                'monthly_alert': 150000,  # INR
                'resource_alert': 1000  # INR per resource
            },
            'optimization': {
                'auto_shutdown_dev': True,
                'auto_scaling_enabled': True,
                'spot_instances_preferred': True,
                'reserved_instances_recommendations': True
            },
            'notifications': {
                'slack_webhook': 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK',
                'email': 'devops@yourcompany.com'
            }
        }
        
        config_path = Path(config_file)
        if config_path.exists():
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        else:
            with open(config_path, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False, indent=2)
            logger.info(f"Created default config file: {config_file}")
        
        return default_config
    
    def setup_cloud_clients(self):
        """Setup cloud provider clients"""
        
        # AWS clients
        try:
            aws_config = self.config.get('aws', {})
            session = boto3.Session(profile_name=aws_config.get('profile', 'default'))
            
            for region in aws_config.get('regions', ['ap-south-1']):
                self.aws_clients[region] = {
                    'ec2': session.client('ec2', region_name=region),
                    'rds': session.client('rds', region_name=region),
                    'elbv2': session.client('elbv2', region_name=region),
                    'elasticache': session.client('elasticache', region_name=region),
                    's3': session.client('s3', region_name=region),
                    'ce': session.client('ce', region_name='us-east-1'),  # Cost Explorer only in us-east-1
                    'cloudwatch': session.client('cloudwatch', region_name=region)
                }
            
            logger.info(f"AWS clients initialized for {len(self.aws_clients)} regions")
            
        except Exception as e:
            logger.warning(f"Failed to initialize AWS clients: {e}")
        
        # Azure clients
        try:
            azure_config = self.config.get('azure', {})
            subscription_id = azure_config.get('subscription_id')
            
            if subscription_id:
                credential = DefaultAzureCredential()
                self.azure_clients['resource'] = ResourceManagementClient(credential, subscription_id)
                self.azure_clients['compute'] = ComputeManagementClient(credential, subscription_id)
                
                logger.info("Azure clients initialized")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Azure clients: {e}")
        
        # GCP clients
        try:
            gcp_config = self.config.get('gcp', {})
            project_id = gcp_config.get('project_id')
            
            if project_id:
                self.gcp_clients['compute'] = compute_v1.InstancesClient()
                self.gcp_clients['project_id'] = project_id
                
                logger.info("GCP clients initialized")
            
        except Exception as e:
            logger.warning(f"Failed to initialize GCP clients: {e}")
    
    def discover_aws_resources(self, region: str) -> List[CloudResource]:
        """Discover AWS resources in a region"""
        
        resources = []
        
        try:
            clients = self.aws_clients.get(region, {})
            
            # EC2 Instances
            if 'ec2' in clients:
                ec2 = clients['ec2']
                response = ec2.describe_instances()
                
                for reservation in response['Reservations']:
                    for instance in reservation['Instances']:
                        if instance['State']['Name'] != 'terminated':
                            # Get instance tags
                            tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                            
                            # Estimate hourly cost (simplified)
                            instance_type = instance['InstanceType']
                            cost_per_hour = self.estimate_aws_instance_cost(instance_type, region)
                            
                            resource = CloudResource(
                                provider=CloudProvider.AWS,
                                resource_type='ec2_instance',
                                resource_id=instance['InstanceId'],
                                name=tags.get('Name', instance['InstanceId']),
                                region=region,
                                status=instance['State']['Name'],
                                cost_per_hour=cost_per_hour,
                                tags=tags,
                                metadata={
                                    'instance_type': instance_type,
                                    'vpc_id': instance.get('VpcId'),
                                    'subnet_id': instance.get('SubnetId'),
                                    'launch_time': instance.get('LaunchTime', '').isoformat() if instance.get('LaunchTime') else '',
                                    'private_ip': instance.get('PrivateIpAddress'),
                                    'public_ip': instance.get('PublicIpAddress')
                                }
                            )
                            
                            resources.append(resource)
            
            # RDS Instances
            if 'rds' in clients:
                rds = clients['rds']
                response = rds.describe_db_instances()
                
                for db_instance in response['DBInstances']:
                    if db_instance['DBInstanceStatus'] != 'deleting':
                        # Estimate hourly cost
                        db_instance_class = db_instance['DBInstanceClass']
                        cost_per_hour = self.estimate_aws_rds_cost(db_instance_class, region)
                        
                        # Get tags
                        try:
                            tags_response = rds.list_tags_for_resource(
                                ResourceName=db_instance['DBInstanceArn']
                            )
                            tags = {tag['Key']: tag['Value'] for tag in tags_response['TagList']}
                        except:
                            tags = {}
                        
                        resource = CloudResource(
                            provider=CloudProvider.AWS,
                            resource_type='rds_instance',
                            resource_id=db_instance['DBInstanceIdentifier'],
                            name=db_instance['DBInstanceIdentifier'],
                            region=region,
                            status=db_instance['DBInstanceStatus'],
                            cost_per_hour=cost_per_hour,
                            tags=tags,
                            metadata={
                                'db_instance_class': db_instance_class,
                                'engine': db_instance['Engine'],
                                'engine_version': db_instance['EngineVersion'],
                                'allocated_storage': db_instance['AllocatedStorage'],
                                'multi_az': db_instance.get('MultiAZ', False),
                                'endpoint': db_instance.get('Endpoint', {}).get('Address')
                            }
                        )
                        
                        resources.append(resource)
            
            # Load Balancers
            if 'elbv2' in clients:
                elbv2 = clients['elbv2']
                response = elbv2.describe_load_balancers()
                
                for lb in response['LoadBalancers']:
                    if lb['State']['Code'] != 'deleting':
                        # Estimate hourly cost
                        cost_per_hour = self.estimate_aws_elb_cost(lb['Type'], region)
                        
                        # Get tags
                        try:
                            tags_response = elbv2.describe_tags(ResourceArns=[lb['LoadBalancerArn']])
                            tags = {}
                            if tags_response['TagDescriptions']:
                                tags = {tag['Key']: tag['Value'] for tag in tags_response['TagDescriptions'][0]['Tags']}
                        except:
                            tags = {}
                        
                        resource = CloudResource(
                            provider=CloudProvider.AWS,
                            resource_type='load_balancer',
                            resource_id=lb['LoadBalancerArn'].split('/')[-1],
                            name=lb['LoadBalancerName'],
                            region=region,
                            status=lb['State']['Code'],
                            cost_per_hour=cost_per_hour,
                            tags=tags,
                            metadata={
                                'type': lb['Type'],
                                'scheme': lb['Scheme'],
                                'vpc_id': lb.get('VpcId'),
                                'dns_name': lb.get('DNSName'),
                                'availability_zones': [az['ZoneName'] for az in lb.get('AvailabilityZones', [])]
                            }
                        )
                        
                        resources.append(resource)
        
        except Exception as e:
            logger.error(f"Failed to discover AWS resources in {region}: {e}")
        
        return resources
    
    def discover_azure_resources(self, region: str) -> List[CloudResource]:
        """Discover Azure resources in a region"""
        
        resources = []
        
        try:
            if 'compute' in self.azure_clients:
                compute_client = self.azure_clients['compute']
                
                # Get all resource groups
                resource_client = self.azure_clients['resource']
                resource_groups = resource_client.resource_groups.list()
                
                for rg in resource_groups:
                    if rg.location.replace(' ', '').lower() == region.lower():
                        # Get VMs in this resource group
                        vms = compute_client.virtual_machines.list(rg.name)
                        
                        for vm in vms:
                            # Get VM size for cost estimation
                            vm_size = vm.hardware_profile.vm_size
                            cost_per_hour = self.estimate_azure_vm_cost(vm_size, region)
                            
                            resource = CloudResource(
                                provider=CloudProvider.AZURE,
                                resource_type='virtual_machine',
                                resource_id=vm.vm_id,
                                name=vm.name,
                                region=region,
                                status=vm.provisioning_state if hasattr(vm, 'provisioning_state') else 'unknown',
                                cost_per_hour=cost_per_hour,
                                tags=vm.tags or {},
                                metadata={
                                    'vm_size': vm_size,
                                    'resource_group': rg.name,
                                    'os_type': vm.storage_profile.os_disk.os_type.value if vm.storage_profile.os_disk.os_type else 'unknown',
                                    'location': vm.location
                                }
                            )
                            
                            resources.append(resource)
        
        except Exception as e:
            logger.error(f"Failed to discover Azure resources in {region}: {e}")
        
        return resources
    
    def discover_gcp_resources(self, region: str) -> List[CloudResource]:
        """Discover GCP resources in a region"""
        
        resources = []
        
        try:
            if 'compute' in self.gcp_clients:
                compute_client = self.gcp_clients['compute']
                project_id = self.gcp_clients['project_id']
                
                # List instances in all zones of the region
                zones_request = compute_v1.ListZonesRequest()
                zones_request.project = project_id
                zones_request.filter = f"region eq .*{region}.*"
                
                zones_client = compute_v1.ZonesClient()
                zones = zones_client.list(zones_request)
                
                for zone in zones:
                    instances_request = compute_v1.ListInstancesRequest()
                    instances_request.project = project_id
                    instances_request.zone = zone.name
                    
                    instances = compute_client.list(instances_request)
                    
                    for instance in instances:
                        # Get machine type for cost estimation
                        machine_type = instance.machine_type.split('/')[-1]
                        cost_per_hour = self.estimate_gcp_instance_cost(machine_type, region)
                        
                        # Extract labels (GCP's equivalent of tags)
                        labels = instance.labels or {}
                        
                        resource = CloudResource(
                            provider=CloudProvider.GCP,
                            resource_type='compute_instance',
                            resource_id=str(instance.id),
                            name=instance.name,
                            region=region,
                            status=instance.status,
                            cost_per_hour=cost_per_hour,
                            tags=labels,
                            metadata={
                                'machine_type': machine_type,
                                'zone': zone.name,
                                'creation_timestamp': instance.creation_timestamp,
                                'network_interfaces': len(instance.network_interfaces),
                                'disks': len(instance.disks)
                            }
                        )
                        
                        resources.append(resource)
        
        except Exception as e:
            logger.error(f"Failed to discover GCP resources in {region}: {e}")
        
        return resources
    
    def estimate_aws_instance_cost(self, instance_type: str, region: str) -> float:
        """Estimate AWS EC2 instance hourly cost in INR"""
        
        # Simplified cost estimation for Mumbai region (ap-south-1)
        # These are approximate costs in INR per hour
        
        cost_map = {
            't2.micro': 0.8,
            't2.small': 1.5,
            't2.medium': 3.0,
            't2.large': 6.0,
            't2.xlarge': 12.0,
            't3.micro': 0.7,
            't3.small': 1.4,
            't3.medium': 2.8,
            't3.large': 5.6,
            't3.xlarge': 11.2,
            't3.2xlarge': 22.4,
            'm5.large': 7.5,
            'm5.xlarge': 15.0,
            'm5.2xlarge': 30.0,
            'm5.4xlarge': 60.0,
            'c5.large': 6.8,
            'c5.xlarge': 13.6,
            'c5.2xlarge': 27.2,
            'r5.large': 10.0,
            'r5.xlarge': 20.0,
            'r5.2xlarge': 40.0
        }
        
        base_cost = cost_map.get(instance_type, 5.0)  # Default cost
        
        # Regional pricing adjustment
        if region != 'ap-south-1':
            base_cost *= 1.1  # 10% premium for other regions
        
        return base_cost
    
    def estimate_aws_rds_cost(self, db_instance_class: str, region: str) -> float:
        """Estimate AWS RDS instance hourly cost in INR"""
        
        cost_map = {
            'db.t2.micro': 1.5,
            'db.t2.small': 2.3,
            'db.t2.medium': 4.6,
            'db.t3.micro': 1.3,
            'db.t3.small': 2.1,
            'db.t3.medium': 4.2,
            'db.t3.large': 8.4,
            'db.r5.large': 18.0,
            'db.r5.xlarge': 36.0,
            'db.r5.2xlarge': 72.0
        }
        
        return cost_map.get(db_instance_class, 10.0)
    
    def estimate_aws_elb_cost(self, lb_type: str, region: str) -> float:
        """Estimate AWS Load Balancer hourly cost in INR"""
        
        if lb_type == 'application':
            return 1.8  # ALB cost per hour
        elif lb_type == 'network':
            return 1.8  # NLB cost per hour
        else:
            return 1.5  # Classic ELB cost per hour
    
    def estimate_azure_vm_cost(self, vm_size: str, region: str) -> float:
        """Estimate Azure VM hourly cost in INR"""
        
        cost_map = {
            'Standard_B1s': 0.9,
            'Standard_B1ms': 1.8,
            'Standard_B2s': 3.6,
            'Standard_B2ms': 7.2,
            'Standard_B4ms': 14.4,
            'Standard_D2s_v3': 8.0,
            'Standard_D4s_v3': 16.0,
            'Standard_D8s_v3': 32.0,
            'Standard_F2s_v2': 7.5,
            'Standard_F4s_v2': 15.0,
            'Standard_F8s_v2': 30.0
        }
        
        return cost_map.get(vm_size, 8.0)
    
    def estimate_gcp_instance_cost(self, machine_type: str, region: str) -> float:
        """Estimate GCP Compute Engine hourly cost in INR"""
        
        cost_map = {
            'f1-micro': 0.5,
            'g1-small': 2.0,
            'n1-standard-1': 3.5,
            'n1-standard-2': 7.0,
            'n1-standard-4': 14.0,
            'n1-standard-8': 28.0,
            'n2-standard-2': 6.5,
            'n2-standard-4': 13.0,
            'n2-standard-8': 26.0,
            'e2-micro': 0.6,
            'e2-small': 1.2,
            'e2-medium': 2.4,
            'e2-standard-2': 5.5,
            'e2-standard-4': 11.0
        }
        
        return cost_map.get(machine_type, 5.0)
    
    async def discover_all_resources(self) -> Dict[str, List[CloudResource]]:
        """Discover resources from all cloud providers concurrently"""
        
        logger.info("Starting multi-cloud resource discovery...")
        all_resources = {}
        
        tasks = []
        
        # AWS discovery tasks
        for region in self.config.get('aws', {}).get('regions', []):
            tasks.append(('aws', region, self.discover_aws_resources(region)))
        
        # Azure discovery tasks
        for region in self.config.get('azure', {}).get('regions', []):
            tasks.append(('azure', region, self.discover_azure_resources(region)))
        
        # GCP discovery tasks
        for region in self.config.get('gcp', {}).get('regions', []):
            tasks.append(('gcp', region, self.discover_gcp_resources(region)))
        
        # Execute discovery in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_task = {
                executor.submit(lambda task=task: task[2]): (task[0], task[1]) 
                for task in tasks
            }
            
            for future in concurrent.futures.as_completed(future_to_task):
                provider, region = future_to_task[future]
                try:
                    resources = future.result()
                    key = f"{provider}_{region}"
                    all_resources[key] = resources
                    logger.info(f"Discovered {len(resources)} resources in {provider} {region}")
                except Exception as e:
                    logger.error(f"Resource discovery failed for {provider} {region}: {e}")
        
        # Store resources
        self.resources = all_resources
        
        return all_resources
    
    def calculate_cost_summary(self) -> Dict[CloudProvider, CostSummary]:
        """Calculate cost summary for each cloud provider"""
        
        summaries = {}
        
        for provider in CloudProvider:
            total_hourly_cost = 0
            resource_count = 0
            expensive_resources = []
            
            # Find all resources for this provider
            for key, resources in self.resources.items():
                if key.startswith(provider.value):
                    for resource in resources:
                        total_hourly_cost += resource.cost_per_hour
                        resource_count += 1
                        
                        if resource.cost_per_hour > 10:  # INR 10+ per hour
                            expensive_resources.append({
                                'name': resource.name,
                                'cost': resource.cost_per_hour,
                                'type': resource.resource_type
                            })
            
            # Sort expensive resources
            expensive_resources.sort(key=lambda x: x['cost'], reverse=True)
            top_expensive = expensive_resources[:5]
            
            # Calculate costs
            daily_cost = total_hourly_cost * 24
            monthly_cost = daily_cost * 30
            yearly_cost = daily_cost * 365
            
            summary = CostSummary(
                provider=provider,
                daily_cost=daily_cost,
                monthly_cost=monthly_cost,
                yearly_cost=yearly_cost,
                currency="INR",
                resources_count=resource_count,
                top_expensive_resources=top_expensive
            )
            
            summaries[provider] = summary
        
        return summaries
    
    def generate_cost_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Generate cost optimization recommendations"""
        
        recommendations = []
        
        for key, resources in self.resources.items():
            provider = key.split('_')[0]
            
            for resource in resources:
                # Check for idle resources (simplified logic)
                if resource.resource_type in ['ec2_instance', 'virtual_machine', 'compute_instance']:
                    if resource.status in ['stopped', 'deallocated'] and resource.tags.get('Environment') == 'dev':
                        recommendations.append({
                            'type': 'idle_resource',
                            'priority': 'high',
                            'resource': resource.name,
                            'provider': provider,
                            'region': resource.region,
                            'potential_savings': resource.cost_per_hour * 24 * 30,  # Monthly savings
                            'recommendation': f"Consider terminating idle {resource.resource_type} '{resource.name}' in development environment",
                            'action': 'terminate_or_schedule'
                        })
                
                # Check for expensive resources
                if resource.cost_per_hour > 50:  # INR 50+ per hour
                    recommendations.append({
                        'type': 'expensive_resource',
                        'priority': 'medium',
                        'resource': resource.name,
                        'provider': provider,
                        'region': resource.region,
                        'current_cost': resource.cost_per_hour,
                        'recommendation': f"Review if {resource.resource_type} '{resource.name}' size/configuration is optimal",
                        'action': 'resize_or_optimize'
                    })
                
                # Check for untagged resources
                if not resource.tags or len(resource.tags) == 0:
                    recommendations.append({
                        'type': 'untagged_resource',
                        'priority': 'low',
                        'resource': resource.name,
                        'provider': provider,
                        'region': resource.region,
                        'recommendation': f"Add proper tags to {resource.resource_type} '{resource.name}' for better cost tracking",
                        'action': 'add_tags'
                    })
        
        # Sort by priority and potential savings
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        recommendations.sort(
            key=lambda x: (
                priority_order.get(x.get('priority', 'low'), 1),
                x.get('potential_savings', 0)
            ),
            reverse=True
        )
        
        return recommendations
    
    def generate_multi_cloud_report(self) -> Dict[str, Any]:
        """Generate comprehensive multi-cloud report"""
        
        cost_summaries = self.calculate_cost_summary()
        recommendations = self.generate_cost_optimization_recommendations()
        
        # Calculate totals
        total_resources = sum(summary.resources_count for summary in cost_summaries.values())
        total_monthly_cost = sum(summary.monthly_cost for summary in cost_summaries.values())
        total_potential_savings = sum(
            rec.get('potential_savings', 0) for rec in recommendations 
            if rec.get('potential_savings')
        )
        
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'summary': {
                'total_resources': total_resources,
                'total_monthly_cost_inr': total_monthly_cost,
                'total_potential_savings_inr': total_potential_savings,
                'providers_count': len([p for p in cost_summaries.values() if p.resources_count > 0])
            },
            'cost_by_provider': {
                provider.value: {
                    'monthly_cost_inr': summary.monthly_cost,
                    'resources_count': summary.resources_count,
                    'daily_cost_inr': summary.daily_cost,
                    'top_expensive_resources': summary.top_expensive_resources
                }
                for provider, summary in cost_summaries.items()
                if summary.resources_count > 0
            },
            'recommendations': recommendations[:20],  # Top 20 recommendations
            'resource_distribution': {
                key: {
                    'count': len(resources),
                    'types': list(set(r.resource_type for r in resources)),
                    'total_cost': sum(r.cost_per_hour * 24 * 30 for r in resources)
                }
                for key, resources in self.resources.items()
                if resources
            }
        }
        
        return report
    
    def send_cost_alerts(self, report: Dict[str, Any]):
        """Send cost alerts based on thresholds"""
        
        thresholds = self.config.get('cost_thresholds', {})
        monthly_cost = report['summary']['total_monthly_cost_inr']
        
        alerts = []
        
        # Check monthly cost threshold
        monthly_threshold = thresholds.get('monthly_alert', 150000)
        if monthly_cost > monthly_threshold:
            alerts.append({
                'type': 'monthly_cost_exceeded',
                'message': f"Monthly cost (₹{monthly_cost:,.0f}) exceeded threshold (₹{monthly_threshold:,.0f})",
                'severity': 'high'
            })
        
        # Check for high-cost resources
        for provider, provider_data in report['cost_by_provider'].items():
            for resource in provider_data.get('top_expensive_resources', []):
                resource_monthly_cost = resource['cost'] * 24 * 30
                resource_threshold = thresholds.get('resource_alert', 1000)
                
                if resource_monthly_cost > resource_threshold:
                    alerts.append({
                        'type': 'expensive_resource',
                        'message': f"{provider.upper()} resource '{resource['name']}' costs ₹{resource_monthly_cost:,.0f}/month",
                        'severity': 'medium'
                    })
        
        # Send alerts if any
        if alerts:
            self.send_slack_notification(alerts, report)
            logger.warning(f"Sent {len(alerts)} cost alerts")
    
    def send_slack_notification(self, alerts: List[Dict], report: Dict[str, Any]):
        """Send Slack notification with alerts and summary"""
        
        webhook_url = self.config.get('notifications', {}).get('slack_webhook')
        if not webhook_url:
            return
        
        # Create Slack message
        total_cost = report['summary']['total_monthly_cost_inr']
        total_resources = report['summary']['total_resources']
        savings = report['summary']['total_potential_savings_inr']
        
        color = "danger" if any(a['severity'] == 'high' for a in alerts) else "warning"
        
        message = {
            "channel": "#infrastructure-alerts",
            "username": "Multi-Cloud Monitor",
            "icon_emoji": ":cloud:",
            "attachments": [
                {
                    "color": color,
                    "title": "Multi-Cloud Infrastructure Report",
                    "fields": [
                        {
                            "title": "Total Monthly Cost",
                            "value": f"₹{total_cost:,.0f}",
                            "short": True
                        },
                        {
                            "title": "Total Resources",
                            "value": str(total_resources),
                            "short": True
                        },
                        {
                            "title": "Potential Savings",
                            "value": f"₹{savings:,.0f}",
                            "short": True
                        },
                        {
                            "title": "Active Providers",
                            "value": str(report['summary']['providers_count']),
                            "short": True
                        }
                    ],
                    "footer": f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}"
                }
            ]
        }
        
        # Add alerts
        if alerts:
            alert_text = "\\n".join([f"• {alert['message']}" for alert in alerts[:5]])
            message["attachments"].append({
                "color": "danger",
                "title": f"🚨 {len(alerts)} Alert(s)",
                "text": alert_text,
                "footer": f"Showing top 5 of {len(alerts)} alerts"
            })
        
        try:
            response = requests.post(webhook_url, json=message, timeout=10)
            if response.status_code == 200:
                logger.info("Slack notification sent successfully")
            else:
                logger.error(f"Failed to send Slack notification: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
    
    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save multi-cloud report to file"""
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"multi_cloud_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Multi-cloud report saved to: {filename}")
        return filename

async def main():
    """Main function to demonstrate multi-cloud management"""
    
    print("🌩️ Multi-Cloud Infrastructure Management System")
    print("=" * 55)
    
    # Initialize multi-cloud manager
    manager = MultiCloudManager()
    
    print("🔍 Discovering resources across all cloud providers...")
    print("This may take a few minutes...")
    
    # Discover all resources
    resources = await manager.discover_all_resources()
    
    # Print discovery summary
    total_resources = sum(len(res_list) for res_list in resources.values())
    print(f"\\n📊 Discovery Complete:")
    print(f"- Total resources discovered: {total_resources}")
    
    for key, res_list in resources.items():
        if res_list:
            provider, region = key.split('_', 1)
            print(f"- {provider.upper()} {region}: {len(res_list)} resources")
    
    # Generate comprehensive report
    print("\\n📋 Generating multi-cloud report...")
    report = manager.generate_multi_cloud_report()
    
    # Print cost summary
    print(f"\\n💰 Cost Summary:")
    print(f"{'='*50}")
    total_monthly = report['summary']['total_monthly_cost_inr']
    potential_savings = report['summary']['total_potential_savings_inr']
    
    print(f"Total Monthly Cost: ₹{total_monthly:,.0f}")
    print(f"Potential Savings: ₹{potential_savings:,.0f}")
    print(f"Active Providers: {report['summary']['providers_count']}")
    
    for provider, data in report['cost_by_provider'].items():
        monthly_cost = data['monthly_cost_inr']
        resource_count = data['resources_count']
        print(f"\\n{provider.upper()}:")
        print(f"  Monthly Cost: ₹{monthly_cost:,.0f}")
        print(f"  Resources: {resource_count}")
        
        if data['top_expensive_resources']:
            print("  Top Expensive Resources:")
            for resource in data['top_expensive_resources'][:3]:
                monthly_resource_cost = resource['cost'] * 24 * 30
                print(f"    - {resource['name']}: ₹{monthly_resource_cost:,.0f}/month")
    
    # Print optimization recommendations
    recommendations = report['recommendations']
    if recommendations:
        print(f"\\n🎯 Top Optimization Recommendations:")
        print(f"{'='*50}")
        
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"{i}. [{rec['priority'].upper()}] {rec['recommendation']}")
            if rec.get('potential_savings'):
                print(f"   Potential savings: ₹{rec['potential_savings']:,.0f}/month")
            print(f"   Action: {rec['action']}")
            print()
    
    # Save report
    report_file = manager.save_report(report)
    print(f"📄 Report saved: {report_file}")
    
    # Send cost alerts
    print(f"\\n🚨 Checking cost thresholds...")
    manager.send_cost_alerts(report)
    
    print(f"\\n🔧 Multi-Cloud Benefits:")
    print("- Unified resource visibility")
    print("- Cross-cloud cost optimization") 
    print("- Automated compliance monitoring")
    print("- Real-time cost alerts")
    print("- Vendor lock-in prevention")
    
    print(f"\\n💡 Optimization Opportunities:")
    high_priority = len([r for r in recommendations if r['priority'] == 'high'])
    medium_priority = len([r for r in recommendations if r['priority'] == 'medium'])
    
    print(f"- High priority actions: {high_priority}")
    print(f"- Medium priority actions: {medium_priority}")
    print(f"- Estimated monthly savings: ₹{potential_savings:,.0f}")
    
    print(f"\\n📈 Indian Enterprise Benefits:")
    print("- Data residency compliance")
    print("- Multi-region disaster recovery")
    print("- Cost optimization for Indian market")
    print("- Rupee-based cost tracking")
    print("- Local support across providers")
    
    print("\\n✅ Multi-cloud management demonstration completed!")

if __name__ == "__main__":
    asyncio.run(main())