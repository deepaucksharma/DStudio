#!/usr/bin/env python3
"""
Kubernetes Cost Allocation System
=================================

Hindi Tech Podcast Series - Episode 60: FinOps & Cost Engineering
Advanced K8s cost allocation with namespace/pod level tracking

Author: Hindi Tech Community
Date: 2025
Version: 1.0

Features:
- Pod-level cost allocation
- Namespace cost tracking
- Resource utilization analysis
- Shared cost distribution
- Department/team cost attribution
- Multi-cluster support

Mumbai Context: K8s cost allocation जैसे Mumbai society का maintenance allocation
- Per flat basis पर electricity, water, security cost
- Common area cost का fair distribution
- Usage-based billing और shared resource costing
"""

import asyncio
import pandas as pd
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from kubernetes import client, config
import requests
import yaml

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PodCostInfo:
    """Pod cost information"""
    pod_name: str
    namespace: str
    node_name: str
    cpu_request: float
    memory_request: float
    cpu_usage: float
    memory_usage: float
    hourly_cost: float
    monthly_cost: float
    team: str
    application: str

class KubernetesCostAllocator:
    """
    Kubernetes Cost Allocation System
    
    Mumbai Context: Society maintenance cost allocation जैसा
    - हर flat का consumption track करना
    - Common facilities की cost को fairly distribute करना
    - Usage patterns के basis पर billing
    """
    
    def __init__(self):
        try:
            config.load_incluster_config()  # If running in cluster
        except:
            config.load_kube_config()  # If running locally
        
        self.v1 = client.CoreV1Api()
        self.metrics_v1beta1 = client.CustomObjectsApi()
        
        # Node pricing (simplified)
        self.node_pricing = {
            'm5.large': {'cpu_hour': 0.048, 'memory_gb_hour': 0.012},
            'm5.xlarge': {'cpu_hour': 0.096, 'memory_gb_hour': 0.024},
            'c5.large': {'cpu_hour': 0.0425, 'memory_gb_hour': 0.0106}
        }
    
    async def get_pod_costs(self) -> List[PodCostInfo]:
        """
        Calculate cost allocation for all pods
        
        Mumbai Context: सभी flats का individual consumption calculate करना
        """
        pod_costs = []
        
        # Get all pods
        pods = self.v1.list_pod_for_all_namespaces()
        
        for pod in pods.items:
            if pod.status.phase != 'Running':
                continue
            
            # Get resource requests
            cpu_request, memory_request = self._get_pod_resource_requests(pod)
            
            # Get actual usage from metrics server
            cpu_usage, memory_usage = await self._get_pod_metrics(pod.metadata.name, pod.metadata.namespace)
            
            # Calculate cost based on node type
            node_cost = self._get_node_cost(pod.spec.node_name)
            hourly_cost = self._calculate_pod_cost(cpu_request, memory_request, node_cost)
            
            # Get team/app info from labels
            team = pod.metadata.labels.get('team', 'unknown')
            app = pod.metadata.labels.get('app', 'unknown')
            
            pod_cost = PodCostInfo(
                pod_name=pod.metadata.name,
                namespace=pod.metadata.namespace,
                node_name=pod.spec.node_name,
                cpu_request=cpu_request,
                memory_request=memory_request,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                hourly_cost=hourly_cost,
                monthly_cost=hourly_cost * 24 * 30,
                team=team,
                application=app
            )
            pod_costs.append(pod_cost)
        
        return pod_costs
    
    def _get_pod_resource_requests(self, pod):
        """Get CPU and memory requests for pod"""
        cpu_request = 0.0
        memory_request = 0.0
        
        for container in pod.spec.containers:
            if container.resources and container.resources.requests:
                # Parse CPU (convert millicores to cores)
                cpu_str = container.resources.requests.get('cpu', '0')
                if 'm' in cpu_str:
                    cpu_request += float(cpu_str.replace('m', '')) / 1000
                else:
                    cpu_request += float(cpu_str or 0)
                
                # Parse memory (convert to GB)
                memory_str = container.resources.requests.get('memory', '0')
                if 'Gi' in memory_str:
                    memory_request += float(memory_str.replace('Gi', ''))
                elif 'Mi' in memory_str:
                    memory_request += float(memory_str.replace('Mi', '')) / 1024
        
        return cpu_request, memory_request
    
    async def _get_pod_metrics(self, pod_name: str, namespace: str) -> tuple:
        """Get actual CPU and memory usage from metrics server"""
        try:
            # Get metrics from metrics server API
            metrics = self.metrics_v1beta1.list_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=namespace,
                plural="pods"
            )
            
            for item in metrics['items']:
                if item['metadata']['name'] == pod_name:
                    cpu_usage = 0.0
                    memory_usage = 0.0
                    
                    for container in item['containers']:
                        # Parse CPU usage
                        cpu_str = container['usage']['cpu']
                        if 'n' in cpu_str:
                            cpu_usage += float(cpu_str.replace('n', '')) / 1000000000
                        elif 'm' in cpu_str:
                            cpu_usage += float(cpu_str.replace('m', '')) / 1000
                        
                        # Parse memory usage  
                        memory_str = container['usage']['memory']
                        if 'Ki' in memory_str:
                            memory_usage += float(memory_str.replace('Ki', '')) / 1024 / 1024
                        elif 'Mi' in memory_str:
                            memory_usage += float(memory_str.replace('Mi', '')) / 1024
                    
                    return cpu_usage, memory_usage
        except Exception as e:
            logger.warning(f"Failed to get metrics for pod {pod_name}: {e}")
        
        return 0.0, 0.0
    
    def _get_node_cost(self, node_name: str) -> Dict[str, float]:
        """Get hourly cost for node"""
        # Simplified - get node instance type from labels
        try:
            node = self.v1.read_node(node_name)
            instance_type = node.metadata.labels.get('node.kubernetes.io/instance-type', 'm5.large')
            return self.node_pricing.get(instance_type, self.node_pricing['m5.large'])
        except:
            return self.node_pricing['m5.large']
    
    def _calculate_pod_cost(self, cpu_request: float, memory_request: float, node_cost: Dict[str, float]) -> float:
        """Calculate hourly cost for pod based on resource requests"""
        cpu_cost = cpu_request * node_cost['cpu_hour']
        memory_cost = memory_request * node_cost['memory_gb_hour']
        return cpu_cost + memory_cost
    
    def generate_cost_allocation_report(self, pod_costs: List[PodCostInfo]) -> str:
        """Generate cost allocation report"""
        df = pd.DataFrame([asdict(pod) for pod in pod_costs])
        
        # Team-wise allocation
        team_costs = df.groupby('team')['monthly_cost'].sum().sort_values(ascending=False)
        
        # Namespace-wise allocation
        namespace_costs = df.groupby('namespace')['monthly_cost'].sum().sort_values(ascending=False)
        
        total_cost = df['monthly_cost'].sum()
        
        report = f"""
Kubernetes Cost Allocation Report
================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY (Mumbai Style)
===============================
यह report आपके K8s cluster का complete cost breakdown है
जैसे Mumbai society में हर flat का maintenance allocation

Total Monthly Cost: ${total_cost:.2f}
Total Pods Analyzed: {len(pod_costs)}
Active Namespaces: {df['namespace'].nunique()}
Teams Using Cluster: {df['team'].nunique()}

TEAM-WISE COST ALLOCATION
========================
"""
        
        for team, cost in team_costs.head(10).items():
            percentage = (cost / total_cost) * 100
            report += f"{team}: ${cost:.2f} ({percentage:.1f}%)\n"
        
        report += f"""

NAMESPACE-WISE ALLOCATION
========================
"""
        
        for namespace, cost in namespace_costs.head(10).items():
            percentage = (cost / total_cost) * 100
            report += f"{namespace}: ${cost:.2f} ({percentage:.1f}%)\n"
        
        report += f"""

OPTIMIZATION OPPORTUNITIES
=========================
• Right-size pod resource requests
• Identify unused namespaces
• Optimize resource utilization
• Consider node consolidation

Mumbai Context: यह society maintenance जैसा है - हर flat fair share pay करे!

Contact: Hindi Tech Community for K8s cost optimization
"""
        
        return report

# Usage Example
def main():
    """Production usage example"""
    try:
        print("☸️  Initializing Kubernetes Cost Allocator...")
        allocator = KubernetesCostAllocator()
        
        print("📊 Analyzing pod costs across cluster...")
        pod_costs = asyncio.run(allocator.get_pod_costs())
        
        if pod_costs:
            total_cost = sum(pod.monthly_cost for pod in pod_costs)
            print(f"Total Monthly Cost: ${total_cost:.2f}")
            print(f"Total Pods: {len(pod_costs)}")
            
            # Generate report
            report = allocator.generate_cost_allocation_report(pod_costs)
            
            with open('k8s_cost_allocation_report.txt', 'w') as f:
                f.write(report)
            
            print("✅ Kubernetes cost allocation completed!")
            print("📄 Report saved to k8s_cost_allocation_report.txt")
        else:
            print("⚠️  No running pods found for cost analysis")
        
    except Exception as e:
        logger.error(f"K8s cost allocation failed: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()