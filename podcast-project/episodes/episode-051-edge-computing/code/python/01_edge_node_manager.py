#!/usr/bin/env python3
"""
Edge Node Manager - एज कंप्यूटिंग नोड्स का ऑर्केस्ट्रेशन
Mumbai Local Train Station Manager की तरह - हर station को manage करना

Real-world inspired by Jio's edge network management across Mumbai
"""

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
import logging
import psutil
import requests
from concurrent.futures import ThreadPoolExecutor

# Configure logging - हिंदी comments के लिए UTF-8 encoding
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NodeStatus(Enum):
    """नोड की स्थिति - train station की तरह"""
    HEALTHY = "स्वस्थ"           # सब ठीक है
    DEGRADED = "क्षीण"          # कुछ समस्या है
    CRITICAL = "गंभीर"         # तुरंत ध्यान चाहिए
    OFFLINE = "ऑफलाइन"        # बिल्कुल down है

@dataclass
class EdgeNode:
    """
    Edge Node representation - Mumbai local train station की तरह
    हर node की अपनी capability और current status
    """
    node_id: str
    location: str               # Mumbai area - Andheri, Bandra, etc.
    cpu_cores: int
    memory_gb: float
    storage_gb: float
    network_bandwidth_mbps: int
    status: NodeStatus
    last_heartbeat: float
    active_workloads: int
    max_workloads: int
    
    def __post_init__(self):
        """Post initialization - additional setup"""
        self.utilization_metrics = {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'storage_percent': 0.0,
            'network_utilization': 0.0
        }

class EdgeNodeManager:
    """
    Edge Node Manager - Mumbai Railway Control Room की तरह
    सभी edge nodes को coordinate और monitor करता है
    """
    
    def __init__(self, region: str = "Mumbai"):
        """
        Initialize edge node manager
        Args:
            region: Geographic region (default: Mumbai)
        """
        self.region = region
        self.nodes: Dict[str, EdgeNode] = {}
        self.workload_queue: List[Dict] = []
        self.health_check_interval = 30  # seconds
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Real-world thresholds based on Jio's edge infrastructure
        self.thresholds = {
            'cpu_critical': 90.0,     # 90% से ज्यादा CPU usage
            'memory_critical': 85.0,   # 85% से ज्यादा memory usage
            'storage_critical': 80.0,  # 80% से ज्यादा storage usage
            'heartbeat_timeout': 120   # 2 minutes without heartbeat
        }
        
        logger.info(f"Edge Node Manager initialized for region: {region}")
    
    def register_node(self, node: EdgeNode) -> bool:
        """
        Register a new edge node - नया station register करना
        जैसे Mumbai में नया local train station add करना
        """
        try:
            if node.node_id in self.nodes:
                logger.warning(f"Node {node.node_id} already registered. Updating...")
            
            self.nodes[node.node_id] = node
            node.last_heartbeat = time.time()
            
            logger.info(f"Node registered: {node.node_id} at {node.location}")
            logger.info(f"Specs: {node.cpu_cores} cores, {node.memory_gb}GB RAM, {node.storage_gb}GB storage")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to register node {node.node_id}: {str(e)}")
            return False
    
    def deregister_node(self, node_id: str) -> bool:
        """
        Deregister a node - station को network से remove करना
        """
        try:
            if node_id not in self.nodes:
                logger.warning(f"Node {node_id} not found for deregistration")
                return False
            
            # First, migrate any active workloads
            node = self.nodes[node_id]
            if node.active_workloads > 0:
                logger.info(f"Migrating {node.active_workloads} workloads from {node_id}")
                self._migrate_workloads(node_id)
            
            del self.nodes[node_id]
            logger.info(f"Node {node_id} deregistered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deregister node {node_id}: {str(e)}")
            return False
    
    async def health_check(self, node_id: str) -> NodeStatus:
        """
        Health check for specific node - station की health check करना
        Mumbai local stations की तरह regular inspection
        """
        try:
            if node_id not in self.nodes:
                return NodeStatus.OFFLINE
                
            node = self.nodes[node_id]
            current_time = time.time()
            
            # Check heartbeat timeout
            if current_time - node.last_heartbeat > self.thresholds['heartbeat_timeout']:
                node.status = NodeStatus.OFFLINE
                logger.warning(f"Node {node_id} heartbeat timeout")
                return NodeStatus.OFFLINE
            
            # Update metrics - actual system metrics simulation
            node.utilization_metrics = self._get_node_metrics(node_id)
            
            # Determine status based on metrics
            cpu_usage = node.utilization_metrics['cpu_percent']
            memory_usage = node.utilization_metrics['memory_percent']
            storage_usage = node.utilization_metrics['storage_percent']
            
            if (cpu_usage > self.thresholds['cpu_critical'] or 
                memory_usage > self.thresholds['memory_critical'] or
                storage_usage > self.thresholds['storage_critical']):
                node.status = NodeStatus.CRITICAL
                logger.error(f"Node {node_id} in CRITICAL state - CPU: {cpu_usage:.1f}%, Memory: {memory_usage:.1f}%, Storage: {storage_usage:.1f}%")
                
            elif (cpu_usage > 70.0 or memory_usage > 70.0 or storage_usage > 60.0):
                node.status = NodeStatus.DEGRADED
                logger.warning(f"Node {node_id} DEGRADED - monitoring closely")
                
            else:
                node.status = NodeStatus.HEALTHY
            
            return node.status
            
        except Exception as e:
            logger.error(f"Health check failed for node {node_id}: {str(e)}")
            return NodeStatus.OFFLINE
    
    def _get_node_metrics(self, node_id: str) -> Dict[str, float]:
        """
        Get actual system metrics for node
        Production में यह actual node से metrics fetch करेगा
        """
        try:
            # In production, this would query actual node metrics
            # For demo, using local system metrics with some randomization
            import random
            
            base_cpu = psutil.cpu_percent(interval=1)
            base_memory = psutil.virtual_memory().percent
            base_disk = psutil.disk_usage('/').percent
            
            # Add some randomization to simulate different nodes
            node_factor = hash(node_id) % 20 - 10  # -10 to +10 variation
            
            return {
                'cpu_percent': max(0, min(100, base_cpu + node_factor)),
                'memory_percent': max(0, min(100, base_memory + node_factor)),
                'storage_percent': max(0, min(100, base_disk + node_factor)),
                'network_utilization': random.uniform(10, 80)
            }
            
        except Exception as e:
            logger.error(f"Failed to get metrics for node {node_id}: {str(e)}")
            return {
                'cpu_percent': 50.0,
                'memory_percent': 50.0, 
                'storage_percent': 50.0,
                'network_utilization': 30.0
            }
    
    async def schedule_workload(self, workload: Dict[str, Any]) -> Optional[str]:
        """
        Schedule workload on best available node
        Mumbai local train की तरह - सबसे suitable platform पे train assign करना
        """
        try:
            # Find best node for workload
            best_node_id = self._find_best_node(workload)
            
            if not best_node_id:
                logger.warning("No suitable node found for workload scheduling")
                return None
            
            node = self.nodes[best_node_id]
            
            # Check if node can handle the workload
            if node.active_workloads >= node.max_workloads:
                logger.warning(f"Node {best_node_id} at capacity")
                return None
            
            # Deploy workload
            success = await self._deploy_workload(best_node_id, workload)
            
            if success:
                node.active_workloads += 1
                logger.info(f"Workload {workload.get('id', 'unknown')} scheduled on node {best_node_id}")
                return best_node_id
            else:
                logger.error(f"Failed to deploy workload on node {best_node_id}")
                return None
                
        except Exception as e:
            logger.error(f"Workload scheduling failed: {str(e)}")
            return None
    
    def _find_best_node(self, workload: Dict[str, Any]) -> Optional[str]:
        """
        Find best node for workload based on requirements and current load
        """
        cpu_required = workload.get('cpu_cores', 1)
        memory_required = workload.get('memory_gb', 1.0)
        storage_required = workload.get('storage_gb', 1.0)
        location_preference = workload.get('location_preference', None)
        
        best_node = None
        best_score = float('inf')
        
        for node_id, node in self.nodes.items():
            # Skip offline or critical nodes
            if node.status in [NodeStatus.OFFLINE, NodeStatus.CRITICAL]:
                continue
            
            # Check basic requirements
            if (node.cpu_cores < cpu_required or 
                node.memory_gb < memory_required or
                node.storage_gb < storage_required):
                continue
            
            # Check capacity
            if node.active_workloads >= node.max_workloads:
                continue
            
            # Calculate score (lower is better)
            utilization_score = (
                node.utilization_metrics['cpu_percent'] +
                node.utilization_metrics['memory_percent'] + 
                node.utilization_metrics['storage_percent']
            ) / 3.0
            
            capacity_score = (node.active_workloads / node.max_workloads) * 100
            
            location_score = 0
            if location_preference and node.location != location_preference:
                location_score = 20  # Penalty for wrong location
            
            total_score = utilization_score + capacity_score + location_score
            
            if total_score < best_score:
                best_score = total_score
                best_node = node_id
        
        return best_node
    
    async def _deploy_workload(self, node_id: str, workload: Dict[str, Any]) -> bool:
        """
        Actually deploy workload on the selected node
        Production में यह actual deployment API call करेगा
        """
        try:
            # Simulate deployment time
            await asyncio.sleep(0.5)
            
            # In production, this would make actual deployment calls
            # For demo, we'll simulate success/failure
            import random
            success_rate = 0.95  # 95% deployment success rate
            
            return random.random() < success_rate
            
        except Exception as e:
            logger.error(f"Workload deployment failed on {node_id}: {str(e)}")
            return False
    
    def _migrate_workloads(self, source_node_id: str):
        """
        Migrate workloads from one node to others
        Emergency situation में workloads को दूसरे nodes पे move करना
        """
        try:
            source_node = self.nodes[source_node_id]
            workloads_to_migrate = source_node.active_workloads
            
            logger.info(f"Migrating {workloads_to_migrate} workloads from {source_node_id}")
            
            # Find alternative nodes
            alternative_nodes = [
                node_id for node_id, node in self.nodes.items()
                if (node_id != source_node_id and 
                    node.status == NodeStatus.HEALTHY and
                    node.active_workloads < node.max_workloads)
            ]
            
            if not alternative_nodes:
                logger.error("No alternative nodes available for migration")
                return
            
            # Distribute workloads across available nodes
            workloads_per_node = workloads_to_migrate // len(alternative_nodes)
            remaining = workloads_to_migrate % len(alternative_nodes)
            
            for i, target_node_id in enumerate(alternative_nodes):
                workloads_to_assign = workloads_per_node
                if i < remaining:
                    workloads_to_assign += 1
                
                target_node = self.nodes[target_node_id]
                target_node.active_workloads += workloads_to_assign
                
                logger.info(f"Migrated {workloads_to_assign} workloads to {target_node_id}")
            
            # Clear source node workloads
            source_node.active_workloads = 0
            
        except Exception as e:
            logger.error(f"Workload migration failed: {str(e)}")
    
    async def monitor_all_nodes(self):
        """
        Continuous monitoring of all nodes
        Mumbai Railway Control Room की तरह 24x7 monitoring
        """
        logger.info("Starting continuous node monitoring...")
        
        while True:
            try:
                # Health check all nodes in parallel
                health_checks = [
                    self.health_check(node_id) 
                    for node_id in self.nodes.keys()
                ]
                
                if health_checks:
                    statuses = await asyncio.gather(*health_checks, return_exceptions=True)
                    
                    # Process results
                    critical_nodes = []
                    offline_nodes = []
                    
                    for i, (node_id, status) in enumerate(zip(self.nodes.keys(), statuses)):
                        if isinstance(status, Exception):
                            logger.error(f"Health check exception for {node_id}: {status}")
                            continue
                            
                        if status == NodeStatus.CRITICAL:
                            critical_nodes.append(node_id)
                        elif status == NodeStatus.OFFLINE:
                            offline_nodes.append(node_id)
                    
                    # Handle critical situations
                    if critical_nodes:
                        logger.warning(f"Critical nodes detected: {critical_nodes}")
                        # In production, trigger alerts and automatic remediation
                    
                    if offline_nodes:
                        logger.error(f"Offline nodes detected: {offline_nodes}")
                        # In production, trigger failover procedures
                
                # Log cluster status summary
                total_nodes = len(self.nodes)
                healthy_nodes = sum(1 for node in self.nodes.values() if node.status == NodeStatus.HEALTHY)
                
                logger.info(f"Cluster Status: {healthy_nodes}/{total_nodes} nodes healthy")
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {str(e)}")
                await asyncio.sleep(5)  # Short delay before retry
    
    def get_cluster_stats(self) -> Dict[str, Any]:
        """
        Get overall cluster statistics
        """
        try:
            total_nodes = len(self.nodes)
            if total_nodes == 0:
                return {"error": "No nodes registered"}
            
            status_counts = {}
            total_cpu_cores = 0
            total_memory_gb = 0
            total_storage_gb = 0
            total_workloads = 0
            total_capacity = 0
            
            avg_cpu_usage = 0
            avg_memory_usage = 0
            avg_storage_usage = 0
            
            for node in self.nodes.values():
                # Count by status
                status_name = node.status.value
                status_counts[status_name] = status_counts.get(status_name, 0) + 1
                
                # Sum resources
                total_cpu_cores += node.cpu_cores
                total_memory_gb += node.memory_gb
                total_storage_gb += node.storage_gb
                total_workloads += node.active_workloads
                total_capacity += node.max_workloads
                
                # Sum usage
                avg_cpu_usage += node.utilization_metrics['cpu_percent']
                avg_memory_usage += node.utilization_metrics['memory_percent']
                avg_storage_usage += node.utilization_metrics['storage_percent']
            
            return {
                "region": self.region,
                "total_nodes": total_nodes,
                "node_status": status_counts,
                "total_resources": {
                    "cpu_cores": total_cpu_cores,
                    "memory_gb": total_memory_gb,
                    "storage_gb": total_storage_gb
                },
                "workload_stats": {
                    "active_workloads": total_workloads,
                    "total_capacity": total_capacity,
                    "utilization_percent": (total_workloads / total_capacity * 100) if total_capacity > 0 else 0
                },
                "average_utilization": {
                    "cpu_percent": avg_cpu_usage / total_nodes,
                    "memory_percent": avg_memory_usage / total_nodes,
                    "storage_percent": avg_storage_usage / total_nodes
                },
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Failed to get cluster stats: {str(e)}")
            return {"error": str(e)}

# Example usage and testing
async def main():
    """
    Demo of Edge Node Manager
    Mumbai local train network की तरह edge nodes का management
    """
    print("🚄 Mumbai Edge Computing Network Manager")
    print("=" * 50)
    
    # Initialize manager
    manager = EdgeNodeManager("Mumbai")
    
    # Create sample nodes - Mumbai के different areas
    nodes = [
        EdgeNode(
            node_id="andheri-east-01",
            location="Andheri East", 
            cpu_cores=8,
            memory_gb=32.0,
            storage_gb=500.0,
            network_bandwidth_mbps=1000,
            status=NodeStatus.HEALTHY,
            last_heartbeat=time.time(),
            active_workloads=0,
            max_workloads=10
        ),
        EdgeNode(
            node_id="bandra-west-01",
            location="Bandra West",
            cpu_cores=16,
            memory_gb=64.0, 
            storage_gb=1000.0,
            network_bandwidth_mbps=2000,
            status=NodeStatus.HEALTHY,
            last_heartbeat=time.time(),
            active_workloads=0,
            max_workloads=20
        ),
        EdgeNode(
            node_id="thane-central-01",
            location="Thane",
            cpu_cores=12,
            memory_gb=48.0,
            storage_gb=750.0,
            network_bandwidth_mbps=1500,
            status=NodeStatus.HEALTHY,
            last_heartbeat=time.time(),
            active_workloads=0,
            max_workloads=15
        )
    ]
    
    # Register nodes
    for node in nodes:
        success = manager.register_node(node)
        print(f"✅ Registered: {node.node_id} - {success}")
    
    # Get initial cluster stats
    stats = manager.get_cluster_stats()
    print(f"\n📊 Cluster Stats:")
    print(f"Total Nodes: {stats['total_nodes']}")
    print(f"Total CPU Cores: {stats['total_resources']['cpu_cores']}")
    print(f"Total Memory: {stats['total_resources']['memory_gb']}GB")
    print(f"Total Storage: {stats['total_resources']['storage_gb']}GB")
    
    # Test workload scheduling
    sample_workloads = [
        {
            "id": "zomato-delivery-app",
            "cpu_cores": 2,
            "memory_gb": 4.0,
            "storage_gb": 10.0,
            "location_preference": "Bandra West"
        },
        {
            "id": "ola-ride-matching",
            "cpu_cores": 4,
            "memory_gb": 8.0,
            "storage_gb": 20.0,
            "location_preference": "Andheri East"
        },
        {
            "id": "paytm-transaction-cache",
            "cpu_cores": 1,
            "memory_gb": 2.0,
            "storage_gb": 5.0,
            "location_preference": "Thane"
        }
    ]
    
    print(f"\n🔄 Scheduling workloads...")
    for workload in sample_workloads:
        assigned_node = await manager.schedule_workload(workload)
        if assigned_node:
            print(f"✅ Workload '{workload['id']}' scheduled on {assigned_node}")
        else:
            print(f"❌ Failed to schedule workload '{workload['id']}'")
    
    # Show updated stats
    updated_stats = manager.get_cluster_stats()
    print(f"\n📊 Updated Cluster Stats:")
    print(f"Active Workloads: {updated_stats['workload_stats']['active_workloads']}")
    print(f"Capacity Utilization: {updated_stats['workload_stats']['utilization_percent']:.1f}%")
    
    # Simulate health monitoring for a short period
    print(f"\n🏥 Running health checks...")
    
    # Run health checks
    for node_id in manager.nodes.keys():
        status = await manager.health_check(node_id)
        node = manager.nodes[node_id]
        print(f"🔍 {node_id}: {status.value}")
        print(f"   CPU: {node.utilization_metrics['cpu_percent']:.1f}%")
        print(f"   Memory: {node.utilization_metrics['memory_percent']:.1f}%")
        print(f"   Storage: {node.utilization_metrics['storage_percent']:.1f}%")
    
    print(f"\n✅ Edge Node Manager demo completed!")
    print(f"🚄 Mumbai edge computing network is operational!")

if __name__ == "__main__":
    asyncio.run(main())