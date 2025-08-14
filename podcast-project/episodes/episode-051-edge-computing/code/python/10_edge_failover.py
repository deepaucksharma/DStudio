#!/usr/bin/env python3
"""
Edge Failover Manager - एज फेलओवर प्रबंधन
Mumbai railway backup system की तरह - जब main system fail हो तो backup activate करना

Real-world inspired by Netflix's chaos engineering, AWS Auto Scaling
Use cases: High availability, disaster recovery, automatic scaling
Cost: Edge failover ₹500 vs Cloud failover ₹5000 per incident
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import threading
from collections import defaultdict, deque
import statistics
import hashlib
import random
import uuid
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NodeState(Enum):
    """Edge node states"""
    HEALTHY = "स्वस्थ"           # Node is healthy and active
    DEGRADED = "क्षीण"          # Node has issues but functional
    CRITICAL = "गंभीर"         # Node is critical, needs attention
    FAILED = "असफल"            # Node has failed
    MAINTENANCE = "रखरखाव"      # Node in maintenance mode
    STANDBY = "स्टैंडबाय"        # Node is on standby

class FailoverType(Enum):
    """Types of failover scenarios"""
    HOT_STANDBY = "हॉट स्टैंडबाय"      # Immediate failover
    WARM_STANDBY = "वार्म स्टैंडबाय"     # Quick failover
    COLD_STANDBY = "कोल्ड स्टैंडबाय"    # Delayed failover
    LOAD_BALANCING = "लोड बैलेंसिंग"   # Distribute load
    GEOGRAPHIC = "भौगोलिक"           # Geographic failover

class FailoverPriority(Enum):
    """Failover priority levels"""
    LOW = "निम्न"               # Low priority services
    MEDIUM = "मध्यम"            # Medium priority services
    HIGH = "उच्च"               # High priority services
    CRITICAL = "गंभीर"           # Critical services

@dataclass
class EdgeNode:
    """Edge node representation for failover management"""
    node_id: str
    hostname: str
    ip_address: str
    location: str
    capacity_cpu: int           # CPU cores
    capacity_memory_gb: float   # Memory in GB
    capacity_storage_gb: float  # Storage in GB
    current_load_cpu: float = 0.0      # Current CPU usage %
    current_load_memory: float = 0.0   # Current memory usage %
    current_load_storage: float = 0.0  # Current storage usage %
    state: NodeState = NodeState.HEALTHY
    last_heartbeat: Optional[datetime] = None
    service_count: int = 0
    failover_group: Optional[str] = None
    priority: FailoverPriority = FailoverPriority.MEDIUM
    backup_nodes: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.node_hash = hashlib.md5(f"{self.node_id}_{self.ip_address}".encode()).hexdigest()[:8]
    
    @property
    def is_healthy(self) -> bool:
        """Check if node is in a healthy state"""
        return self.state in [NodeState.HEALTHY, NodeState.DEGRADED]
    
    @property
    def can_accept_load(self) -> bool:
        """Check if node can accept additional load"""
        return (self.is_healthy and 
                self.current_load_cpu < 80.0 and 
                self.current_load_memory < 80.0 and
                self.current_load_storage < 90.0)

@dataclass
class EdgeService:
    """Edge service requiring failover protection"""
    service_id: str
    service_name: str
    primary_node: str
    backup_nodes: List[str]
    failover_type: FailoverType
    priority: FailoverPriority
    resource_requirements: Dict[str, float]  # CPU, memory, storage requirements
    health_check_endpoint: str
    recovery_time_objective: int  # RTO in seconds
    recovery_point_objective: int  # RPO in seconds
    is_active: bool = True
    current_node: Optional[str] = None
    failover_count: int = 0
    last_failover: Optional[datetime] = None

@dataclass
class FailoverEvent:
    """Failover event record"""
    event_id: str
    timestamp: datetime
    event_type: str  # node_failure, service_failover, recovery
    source_node: str
    target_node: Optional[str]
    affected_services: List[str]
    trigger_reason: str
    resolution_time_seconds: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None

class EdgeFailoverManager:
    """
    Edge Failover Manager - Mumbai Railway Control Room की तरह
    सभी edge nodes और services का failover management
    """
    
    def __init__(self, manager_id: str, location: str = "Mumbai"):
        """
        Initialize Edge Failover Manager
        Args:
            manager_id: Unique manager identifier
            location: Geographic location
        """
        self.manager_id = manager_id
        self.location = location
        
        # Node and service management
        self.edge_nodes: Dict[str, EdgeNode] = {}
        self.edge_services: Dict[str, EdgeService] = {}
        self.failover_groups: Dict[str, List[str]] = {}
        
        # Failover tracking
        self.failover_events: deque = deque(maxlen=10000)
        self.active_failovers: Dict[str, FailoverEvent] = {}
        self.recovery_queue = asyncio.Queue()
        
        # Monitoring and health checking
        self.heartbeat_interval = 10  # seconds
        self.health_check_timeout = 5  # seconds
        self.failure_threshold = 3    # consecutive failures before marking as failed
        
        # Performance metrics
        self.stats = {
            'total_nodes': 0,
            'healthy_nodes': 0,
            'failed_nodes': 0,
            'total_services': 0,
            'active_services': 0,
            'total_failovers': 0,
            'successful_failovers': 0,
            'failed_failovers': 0,
            'avg_failover_time_seconds': 0.0,
            'avg_recovery_time_seconds': 0.0,
            'uptime_start': datetime.now(),
            'failover_times': deque(maxlen=100),
            'recovery_times': deque(maxlen=100)
        }
        
        # Threading and async
        self.running = False
        self.monitor_tasks = []
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Mumbai-specific failover configurations
        self._initialize_mumbai_failover_config()
        
        logger.info(f"Edge Failover Manager initialized: {manager_id} @ {location}")
    
    def _initialize_mumbai_failover_config(self):
        """Initialize Mumbai-specific failover configurations"""
        
        # Failover group configurations for Mumbai zones
        self.failover_groups = {
            'mumbai_central': ['node_central_01', 'node_central_02', 'node_central_backup'],
            'mumbai_south': ['node_south_01', 'node_south_02', 'node_south_backup'],
            'mumbai_north': ['node_north_01', 'node_north_02', 'node_north_backup'],
            'mumbai_west': ['node_west_01', 'node_west_02', 'node_west_backup'],
            'mumbai_east': ['node_east_01', 'node_east_02', 'node_east_backup']
        }
        
        # Service priorities for Mumbai applications
        self.service_priorities = {
            'payment_gateway': FailoverPriority.CRITICAL,
            'user_authentication': FailoverPriority.CRITICAL,
            'real_time_trading': FailoverPriority.CRITICAL,
            'video_streaming': FailoverPriority.HIGH,
            'api_gateway': FailoverPriority.HIGH,
            'web_frontend': FailoverPriority.MEDIUM,
            'batch_processing': FailoverPriority.LOW,
            'analytics': FailoverPriority.LOW
        }
        
        # Failover strategies by service type
        self.failover_strategies = {
            'critical_services': {
                'type': FailoverType.HOT_STANDBY,
                'rto_seconds': 30,   # 30 seconds max downtime
                'rpo_seconds': 0,    # No data loss
                'backup_ratio': 2    # 2 backups per primary
            },
            'high_priority': {
                'type': FailoverType.WARM_STANDBY,
                'rto_seconds': 120,  # 2 minutes max downtime
                'rpo_seconds': 60,   # 1 minute data loss acceptable
                'backup_ratio': 1    # 1 backup per primary
            },
            'standard_services': {
                'type': FailoverType.COLD_STANDBY,
                'rto_seconds': 300,  # 5 minutes max downtime
                'rpo_seconds': 300,  # 5 minutes data loss acceptable
                'backup_ratio': 1    # 1 backup per primary group
            }
        }
        
        logger.info("Mumbai failover configurations initialized")
    
    async def start(self):
        """Start the failover manager"""
        if self.running:
            logger.warning("Failover manager already running")
            return
        
        self.running = True
        
        # Start monitoring tasks
        self.monitor_tasks = [
            asyncio.create_task(self._node_health_monitor_loop()),
            asyncio.create_task(self._service_health_monitor_loop()),
            asyncio.create_task(self._failover_executor_loop()),
            asyncio.create_task(self._recovery_manager_loop()),
            asyncio.create_task(self._metrics_collector_loop())
        ]
        
        logger.info("Edge Failover Manager started")
    
    async def stop(self):
        """Stop the failover manager"""
        if not self.running:
            return
        
        self.running = False
        
        # Cancel monitoring tasks
        for task in self.monitor_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        try:
            await asyncio.gather(*self.monitor_tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error stopping monitor tasks: {str(e)}")
        
        logger.info("Edge Failover Manager stopped")
    
    def register_edge_node(self, node: EdgeNode) -> bool:
        """
        Register edge node for failover management
        Mumbai railway station को network में add करने की तरह
        """
        try:
            if node.node_id in self.edge_nodes:
                logger.info(f"Node {node.node_id} already registered, updating...")
            else:
                self.stats['total_nodes'] += 1
            
            node.last_heartbeat = datetime.now()
            node.state = NodeState.HEALTHY
            self.edge_nodes[node.node_id] = node
            
            # Update healthy nodes count
            self._update_node_counts()
            
            logger.info(f"Edge node registered: {node.node_id} @ {node.location}")
            return True
            
        except Exception as e:
            logger.error(f"Node registration failed: {str(e)}")
            return False
    
    def register_edge_service(self, service: EdgeService) -> bool:
        """
        Register edge service for failover protection
        Mumbai train service को failover protection देने की तरह
        """
        try:
            if service.service_id in self.edge_services:
                logger.info(f"Service {service.service_id} already registered, updating...")
            else:
                self.stats['total_services'] += 1
            
            # Validate primary and backup nodes exist
            if service.primary_node not in self.edge_nodes:
                logger.error(f"Primary node {service.primary_node} not found")
                return False
            
            for backup_node in service.backup_nodes:
                if backup_node not in self.edge_nodes:
                    logger.error(f"Backup node {backup_node} not found")
                    return False
            
            service.current_node = service.primary_node
            self.edge_services[service.service_id] = service
            
            # Update primary node service count
            self.edge_nodes[service.primary_node].service_count += 1
            
            # Update active services count
            self._update_service_counts()
            
            logger.info(f"Edge service registered: {service.service_id} -> {service.primary_node}")
            return True
            
        except Exception as e:
            logger.error(f"Service registration failed: {str(e)}")
            return False
    
    async def trigger_manual_failover(self, service_id: str, target_node: str, reason: str = "Manual failover") -> bool:
        """
        Manually trigger failover for a service
        Emergency situation में manual train rerouting की तरह
        """
        try:
            if service_id not in self.edge_services:
                logger.error(f"Service {service_id} not found")
                return False
            
            service = self.edge_services[service_id]
            
            if target_node not in self.edge_nodes:
                logger.error(f"Target node {target_node} not found")
                return False
            
            if not self.edge_nodes[target_node].can_accept_load:
                logger.error(f"Target node {target_node} cannot accept additional load")
                return False
            
            logger.info(f"Manual failover triggered: {service_id} -> {target_node}")
            
            # Execute failover
            success = await self._execute_failover(service, target_node, reason)
            
            return success
            
        except Exception as e:
            logger.error(f"Manual failover failed: {str(e)}")
            return False
    
    async def _node_health_monitor_loop(self):
        """
        Monitor health of all edge nodes
        Mumbai railway station monitoring की तरह
        """
        logger.info("Node health monitor started")
        
        while self.running:
            try:
                current_time = datetime.now()
                failed_nodes = []
                
                for node_id, node in self.edge_nodes.items():
                    # Check heartbeat timeout
                    if node.last_heartbeat:
                        time_since_heartbeat = current_time - node.last_heartbeat
                        
                        if time_since_heartbeat.total_seconds() > (self.heartbeat_interval * self.failure_threshold):
                            if node.state != NodeState.FAILED:
                                logger.error(f"Node {node_id} failed - no heartbeat for {time_since_heartbeat.total_seconds():.1f}s")
                                await self._handle_node_failure(node_id, "Heartbeat timeout")
                    
                    # Simulate heartbeat updates (in production, nodes would send actual heartbeats)
                    await self._simulate_node_heartbeat(node)
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Node health monitor error: {str(e)}")
                await asyncio.sleep(5)
        
        logger.info("Node health monitor stopped")
    
    async def _simulate_node_heartbeat(self, node: EdgeNode):
        """Simulate node heartbeat and health metrics"""
        try:
            # Simulate 5% chance of node having issues
            if random.random() < 0.05:
                if node.state == NodeState.HEALTHY:
                    node.state = NodeState.DEGRADED
                    logger.warning(f"Node {node.node_id} degraded")
                elif node.state == NodeState.DEGRADED and random.random() < 0.3:
                    node.state = NodeState.CRITICAL
                    logger.error(f"Node {node.node_id} critical")
            else:
                # Recovery simulation
                if node.state == NodeState.CRITICAL and random.random() < 0.7:
                    node.state = NodeState.DEGRADED
                    logger.info(f"Node {node.node_id} recovered to degraded")
                elif node.state == NodeState.DEGRADED and random.random() < 0.8:
                    node.state = NodeState.HEALTHY
                    logger.info(f"Node {node.node_id} recovered to healthy")
            
            # Update load metrics (simulate varying load)
            node.current_load_cpu = max(10.0, min(95.0, node.current_load_cpu + random.uniform(-5, 5)))
            node.current_load_memory = max(20.0, min(90.0, node.current_load_memory + random.uniform(-3, 3)))
            node.current_load_storage = max(30.0, min(95.0, node.current_load_storage + random.uniform(-1, 1)))
            
            # Update heartbeat
            node.last_heartbeat = datetime.now()
            
        except Exception as e:
            logger.error(f"Heartbeat simulation failed for {node.node_id}: {str(e)}")
    
    async def _service_health_monitor_loop(self):
        """Monitor health of all edge services"""
        logger.info("Service health monitor started")
        
        while self.running:
            try:
                for service_id, service in self.edge_services.items():
                    if not service.is_active:
                        continue
                    
                    # Check if current node is healthy
                    current_node = self.edge_nodes.get(service.current_node)
                    if not current_node or not current_node.is_healthy:
                        logger.warning(f"Service {service_id} node {service.current_node} is unhealthy")
                        await self._trigger_service_failover(service, "Node unhealthy")
                    
                    # Simulate service health checks
                    await self._simulate_service_health_check(service)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Service health monitor error: {str(e)}")
                await asyncio.sleep(10)
        
        logger.info("Service health monitor stopped")
    
    async def _simulate_service_health_check(self, service: EdgeService):
        """Simulate service health check"""
        try:
            # Simulate 2% chance of service failure
            if random.random() < 0.02:
                logger.error(f"Service {service.service_id} health check failed")
                await self._trigger_service_failover(service, "Health check failure")
                
        except Exception as e:
            logger.error(f"Service health check simulation failed: {str(e)}")
    
    async def _handle_node_failure(self, node_id: str, reason: str):
        """
        Handle node failure and trigger failovers for affected services
        Mumbai station failure में सभी trains को reroute करने की तरह
        """
        try:
            node = self.edge_nodes.get(node_id)
            if not node:
                return
            
            # Mark node as failed
            node.state = NodeState.FAILED
            self.stats['failed_nodes'] += 1
            
            # Find all services running on this node
            affected_services = [
                service for service in self.edge_services.values()
                if service.current_node == node_id and service.is_active
            ]
            
            logger.error(f"Node {node_id} failed, affecting {len(affected_services)} services")
            
            # Create failover event
            event = FailoverEvent(
                event_id=f"node_failure_{node_id}_{int(time.time())}",
                timestamp=datetime.now(),
                event_type="node_failure",
                source_node=node_id,
                target_node=None,
                affected_services=[s.service_id for s in affected_services],
                trigger_reason=reason
            )
            
            self.failover_events.append(event)
            self.active_failovers[event.event_id] = event
            
            # Trigger failover for all affected services
            for service in affected_services:
                await self._trigger_service_failover(service, f"Node failure: {reason}")
            
            self._update_node_counts()
            
        except Exception as e:
            logger.error(f"Node failure handling failed: {str(e)}")
    
    async def _trigger_service_failover(self, service: EdgeService, reason: str):
        """
        Trigger failover for a specific service
        Mumbai train को alternate route पे भेजने की तरह
        """
        try:
            # Find best backup node
            best_backup = await self._find_best_backup_node(service)
            
            if not best_backup:
                logger.error(f"No suitable backup node found for service {service.service_id}")
                return False
            
            logger.info(f"Triggering failover: {service.service_id} -> {best_backup}")
            
            # Execute failover
            success = await self._execute_failover(service, best_backup, reason)
            
            return success
            
        except Exception as e:
            logger.error(f"Service failover trigger failed: {str(e)}")
            return False
    
    async def _find_best_backup_node(self, service: EdgeService) -> Optional[str]:
        """
        Find best available backup node for service
        Mumbai train के लिए best alternate route find करने की तरह
        """
        try:
            available_backups = []
            
            # Check backup nodes in order of preference
            for backup_node_id in service.backup_nodes:
                backup_node = self.edge_nodes.get(backup_node_id)
                
                if (backup_node and 
                    backup_node.can_accept_load and
                    backup_node_id != service.current_node):
                    
                    # Calculate suitability score
                    score = self._calculate_node_suitability_score(backup_node, service)
                    available_backups.append((backup_node_id, score))
            
            if not available_backups:
                # Try any healthy node as last resort
                for node_id, node in self.edge_nodes.items():
                    if (node.can_accept_load and 
                        node_id != service.current_node and
                        node_id not in service.backup_nodes):
                        
                        score = self._calculate_node_suitability_score(node, service)
                        available_backups.append((node_id, score * 0.5))  # Lower score for non-preferred nodes
            
            if available_backups:
                # Sort by score (higher is better)
                available_backups.sort(key=lambda x: x[1], reverse=True)
                return available_backups[0][0]
            
            return None
            
        except Exception as e:
            logger.error(f"Backup node selection failed: {str(e)}")
            return None
    
    def _calculate_node_suitability_score(self, node: EdgeNode, service: EdgeService) -> float:
        """Calculate how suitable a node is for hosting a service"""
        try:
            score = 100.0
            
            # Penalize based on current load
            load_penalty = (node.current_load_cpu + node.current_load_memory + node.current_load_storage) / 3.0
            score -= load_penalty * 0.5
            
            # Bonus for healthy state
            if node.state == NodeState.HEALTHY:
                score += 20.0
            elif node.state == NodeState.DEGRADED:
                score -= 10.0
            
            # Penalize for high service count
            score -= node.service_count * 5.0
            
            # Location preference (same location is better)
            primary_node = self.edge_nodes.get(service.primary_node)
            if primary_node and node.location == primary_node.location:
                score += 15.0
            
            # Resource capacity check
            cpu_req = service.resource_requirements.get('cpu_cores', 1)
            memory_req = service.resource_requirements.get('memory_gb', 1.0)
            
            if node.capacity_cpu < cpu_req or node.capacity_memory_gb < memory_req:
                score -= 50.0  # Heavy penalty for insufficient resources
            
            return max(0.0, score)
            
        except Exception as e:
            logger.error(f"Suitability score calculation failed: {str(e)}")
            return 0.0
    
    async def _execute_failover(self, service: EdgeService, target_node: str, reason: str) -> bool:
        """
        Execute actual failover process
        Mumbai train को new platform पे shift करने की तरह
        """
        start_time = time.time()
        
        try:
            old_node = service.current_node
            
            # Create failover event
            event = FailoverEvent(
                event_id=f"failover_{service.service_id}_{int(time.time())}",
                timestamp=datetime.now(),
                event_type="service_failover",
                source_node=old_node,
                target_node=target_node,
                affected_services=[service.service_id],
                trigger_reason=reason
            )
            
            self.failover_events.append(event)
            self.active_failovers[event.event_id] = event
            
            logger.info(f"Executing failover: {service.service_id} from {old_node} to {target_node}")
            
            # Simulate failover process based on type
            failover_delay = self._get_failover_delay(service.failover_type)
            await asyncio.sleep(failover_delay)
            
            # Update service current node
            service.current_node = target_node
            service.failover_count += 1
            service.last_failover = datetime.now()
            
            # Update node service counts
            if old_node and old_node in self.edge_nodes:
                self.edge_nodes[old_node].service_count = max(0, self.edge_nodes[old_node].service_count - 1)
            
            self.edge_nodes[target_node].service_count += 1
            
            # Complete the event
            execution_time = time.time() - start_time
            event.resolution_time_seconds = execution_time
            event.success = True
            
            # Update statistics
            self.stats['total_failovers'] += 1
            self.stats['successful_failovers'] += 1
            self.stats['failover_times'].append(execution_time)
            
            if self.stats['failover_times']:
                self.stats['avg_failover_time_seconds'] = statistics.mean(self.stats['failover_times'])
            
            # Remove from active failovers
            del self.active_failovers[event.event_id]
            
            logger.info(f"Failover completed: {service.service_id} -> {target_node} in {execution_time:.2f}s")
            
            # Add to recovery queue for monitoring
            await self.recovery_queue.put((service.service_id, event))
            
            return True
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Mark event as failed
            if 'event' in locals():
                event.success = False
                event.error_message = str(e)
                event.resolution_time_seconds = execution_time
                
                if event.event_id in self.active_failovers:
                    del self.active_failovers[event.event_id]
            
            self.stats['total_failovers'] += 1
            self.stats['failed_failovers'] += 1
            
            logger.error(f"Failover execution failed: {str(e)}")
            return False
    
    def _get_failover_delay(self, failover_type: FailoverType) -> float:
        """Get failover delay based on type"""
        delays = {
            FailoverType.HOT_STANDBY: 0.1,    # 100ms - very fast
            FailoverType.WARM_STANDBY: 2.0,   # 2 seconds
            FailoverType.COLD_STANDBY: 10.0,  # 10 seconds
            FailoverType.LOAD_BALANCING: 0.5, # 500ms
            FailoverType.GEOGRAPHIC: 5.0      # 5 seconds
        }
        return delays.get(failover_type, 2.0)
    
    async def _failover_executor_loop(self):
        """Background failover execution management"""
        logger.info("Failover executor started")
        
        while self.running:
            try:
                # Monitor active failovers for timeouts
                current_time = datetime.now()
                timeout_events = []
                
                for event_id, event in self.active_failovers.items():
                    age = (current_time - event.timestamp).total_seconds()
                    if age > 300:  # 5 minutes timeout
                        timeout_events.append(event_id)
                        logger.error(f"Failover timeout: {event_id}")
                
                # Clean up timed out events
                for event_id in timeout_events:
                    if event_id in self.active_failovers:
                        event = self.active_failovers[event_id]
                        event.success = False
                        event.error_message = "Failover timeout"
                        del self.active_failovers[event_id]
                        self.stats['failed_failovers'] += 1
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Failover executor error: {str(e)}")
                await asyncio.sleep(10)
        
        logger.info("Failover executor stopped")
    
    async def _recovery_manager_loop(self):
        """Monitor service recovery after failover"""
        logger.info("Recovery manager started")
        
        while self.running:
            try:
                # Process recovery queue
                try:
                    service_id, failover_event = await asyncio.wait_for(
                        self.recovery_queue.get(), timeout=1.0
                    )
                    
                    # Monitor service recovery
                    await self._monitor_service_recovery(service_id, failover_event)
                    
                except asyncio.TimeoutError:
                    continue
                
            except Exception as e:
                logger.error(f"Recovery manager error: {str(e)}")
                await asyncio.sleep(10)
        
        logger.info("Recovery manager stopped")
    
    async def _monitor_service_recovery(self, service_id: str, failover_event: FailoverEvent):
        """Monitor service recovery after failover"""
        try:
            service = self.edge_services.get(service_id)
            if not service:
                return
            
            logger.info(f"Monitoring recovery for service {service_id}")
            
            # Wait for service to stabilize
            recovery_start = time.time()
            max_recovery_time = service.recovery_time_objective
            
            while time.time() - recovery_start < max_recovery_time:
                # Simulate service health check
                if random.random() < 0.9:  # 90% chance service is healthy
                    recovery_time = time.time() - recovery_start
                    
                    # Log successful recovery
                    recovery_event = FailoverEvent(
                        event_id=f"recovery_{service_id}_{int(time.time())}",
                        timestamp=datetime.now(),
                        event_type="service_recovery",
                        source_node=failover_event.target_node,
                        target_node=None,
                        affected_services=[service_id],
                        trigger_reason=f"Recovery after failover {failover_event.event_id}",
                        resolution_time_seconds=recovery_time,
                        success=True
                    )
                    
                    self.failover_events.append(recovery_event)
                    self.stats['recovery_times'].append(recovery_time)
                    
                    if self.stats['recovery_times']:
                        self.stats['avg_recovery_time_seconds'] = statistics.mean(self.stats['recovery_times'])
                    
                    logger.info(f"Service {service_id} recovered in {recovery_time:.2f}s")
                    return
                
                await asyncio.sleep(5)  # Check every 5 seconds
            
            # Recovery timed out
            logger.error(f"Service {service_id} recovery timed out after {max_recovery_time}s")
            
        except Exception as e:
            logger.error(f"Recovery monitoring failed: {str(e)}")
    
    async def _metrics_collector_loop(self):
        """Collect and update performance metrics"""
        logger.info("Metrics collector started")
        
        while self.running:
            try:
                # Update node counts
                self._update_node_counts()
                self._update_service_counts()
                
                # Clean up old events (keep last 24 hours)
                cutoff_time = datetime.now() - timedelta(hours=24)
                while (self.failover_events and 
                       self.failover_events[0].timestamp < cutoff_time):
                    self.failover_events.popleft()
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Metrics collector error: {str(e)}")
                await asyncio.sleep(30)
        
        logger.info("Metrics collector stopped")
    
    def _update_node_counts(self):
        """Update node health statistics"""
        healthy_nodes = sum(1 for node in self.edge_nodes.values() if node.state == NodeState.HEALTHY)
        failed_nodes = sum(1 for node in self.edge_nodes.values() if node.state == NodeState.FAILED)
        
        self.stats['healthy_nodes'] = healthy_nodes
        self.stats['failed_nodes'] = failed_nodes
    
    def _update_service_counts(self):
        """Update service statistics"""
        active_services = sum(1 for service in self.edge_services.values() if service.is_active)
        self.stats['active_services'] = active_services
    
    def get_failover_stats(self) -> Dict[str, Any]:
        """Get comprehensive failover management statistics"""
        try:
            current_time = datetime.now()
            uptime = current_time - self.stats['uptime_start']
            
            # Node statistics
            node_states = defaultdict(int)
            for node in self.edge_nodes.values():
                node_states[node.state.value] += 1
            
            # Service statistics
            service_priorities = defaultdict(int)
            service_failover_counts = defaultdict(int)
            
            for service in self.edge_services.values():
                service_priorities[service.priority.value] += 1
                if service.failover_count > 0:
                    service_failover_counts[service.service_id] = service.failover_count
            
            # Recent events summary
            recent_events = [
                event for event in list(self.failover_events)[-100:]  # Last 100 events
            ]
            
            event_types = defaultdict(int)
            for event in recent_events:
                event_types[event.event_type] += 1
            
            return {
                "manager_info": {
                    "manager_id": self.manager_id,
                    "location": self.location,
                    "uptime_hours": round(uptime.total_seconds() / 3600, 2),
                    "status": "running" if self.running else "stopped"
                },
                "node_statistics": {
                    "total_nodes": self.stats['total_nodes'],
                    "healthy_nodes": self.stats['healthy_nodes'],
                    "failed_nodes": self.stats['failed_nodes'],
                    "node_states": dict(node_states)
                },
                "service_statistics": {
                    "total_services": self.stats['total_services'],
                    "active_services": self.stats['active_services'],
                    "services_by_priority": dict(service_priorities),
                    "services_with_failovers": len(service_failover_counts)
                },
                "failover_statistics": {
                    "total_failovers": self.stats['total_failovers'],
                    "successful_failovers": self.stats['successful_failovers'],
                    "failed_failovers": self.stats['failed_failovers'],
                    "success_rate_percent": (
                        (self.stats['successful_failovers'] / self.stats['total_failovers'] * 100)
                        if self.stats['total_failovers'] > 0 else 100
                    ),
                    "avg_failover_time_seconds": round(self.stats['avg_failover_time_seconds'], 2),
                    "avg_recovery_time_seconds": round(self.stats['avg_recovery_time_seconds'], 2),
                    "active_failovers": len(self.active_failovers)
                },
                "recent_events": {
                    "total_recent_events": len(recent_events),
                    "events_by_type": dict(event_types),
                    "last_event_time": recent_events[-1].timestamp.isoformat() if recent_events else None
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get failover stats: {str(e)}")
            return {"error": str(e)}

# Example usage and comprehensive testing
async def main():
    """
    Comprehensive Edge Failover Manager testing
    Mumbai railway backup system demonstration
    """
    print("🔄 Edge Failover Manager - Mumbai Railway Backup System")
    print("=" * 60)
    
    # Initialize failover manager
    failover_manager = EdgeFailoverManager("mumbai-failover-01", "Mumbai Central")
    await failover_manager.start()
    
    print(f"✅ Failover Manager started: {failover_manager.manager_id}")
    print(f"📍 Location: {failover_manager.location}")
    
    # Register Mumbai edge nodes
    print(f"\n🖥️ Registering Mumbai Edge Nodes...")
    
    mumbai_nodes = [
        EdgeNode(
            node_id="mumbai_primary_01",
            hostname="mumbai-edge-primary-01",
            ip_address="192.168.1.101",
            location="Mumbai Central",
            capacity_cpu=16,
            capacity_memory_gb=64.0,
            capacity_storage_gb=1000.0,
            current_load_cpu=45.0,
            current_load_memory=60.0,
            current_load_storage=30.0,
            failover_group="mumbai_central",
            priority=FailoverPriority.CRITICAL
        ),
        EdgeNode(
            node_id="mumbai_backup_01",
            hostname="mumbai-edge-backup-01",
            ip_address="192.168.1.102",
            location="Mumbai Central",
            capacity_cpu=12,
            capacity_memory_gb=48.0,
            capacity_storage_gb=750.0,
            current_load_cpu=20.0,
            current_load_memory=25.0,
            current_load_storage=15.0,
            failover_group="mumbai_central",
            priority=FailoverPriority.HIGH,
            backup_nodes=["mumbai_primary_01"]
        ),
        EdgeNode(
            node_id="mumbai_secondary_01",
            hostname="mumbai-edge-secondary-01",
            ip_address="192.168.1.103",
            location="Navi Mumbai",
            capacity_cpu=8,
            capacity_memory_gb=32.0,
            capacity_storage_gb=500.0,
            current_load_cpu=35.0,
            current_load_memory=40.0,
            current_load_storage=25.0,
            failover_group="mumbai_south",
            priority=FailoverPriority.MEDIUM
        ),
        EdgeNode(
            node_id="mumbai_emergency_01",
            hostname="mumbai-edge-emergency-01",
            ip_address="192.168.1.104",
            location="Mumbai West",
            capacity_cpu=6,
            capacity_memory_gb=24.0,
            capacity_storage_gb=300.0,
            current_load_cpu=10.0,
            current_load_memory=15.0,
            current_load_storage=10.0,
            state=NodeState.STANDBY,
            priority=FailoverPriority.LOW
        )
    ]
    
    # Register nodes
    for node in mumbai_nodes:
        success = failover_manager.register_edge_node(node)
        state_emoji = {"स्वस्थ": "🟢", "क्षीण": "🟡", "गंभीर": "🟠", "असफल": "🔴", "रखरखाव": "🔵", "स्टैंडबाय": "⚫"}
        status_emoji = "✅" if success else "❌"
        
        print(f"{status_emoji} {node.node_id}: {node.ip_address}")
        print(f"   State: {state_emoji[node.state.value]} | CPU: {node.capacity_cpu} cores | Memory: {node.capacity_memory_gb}GB")
        print(f"   Load: CPU {node.current_load_cpu}%, Memory {node.current_load_memory}%")
    
    # Register edge services
    print(f"\n🚀 Registering Mumbai Edge Services...")
    
    mumbai_services = [
        EdgeService(
            service_id="mumbai_payment_gateway",
            service_name="Mumbai Payment Gateway",
            primary_node="mumbai_primary_01",
            backup_nodes=["mumbai_backup_01", "mumbai_secondary_01"],
            failover_type=FailoverType.HOT_STANDBY,
            priority=FailoverPriority.CRITICAL,
            resource_requirements={"cpu_cores": 4, "memory_gb": 16.0, "storage_gb": 100.0},
            health_check_endpoint="/health",
            recovery_time_objective=30,  # 30 seconds
            recovery_point_objective=0   # No data loss
        ),
        EdgeService(
            service_id="mumbai_user_auth",
            service_name="Mumbai User Authentication",
            primary_node="mumbai_primary_01",
            backup_nodes=["mumbai_backup_01"],
            failover_type=FailoverType.WARM_STANDBY,
            priority=FailoverPriority.CRITICAL,
            resource_requirements={"cpu_cores": 2, "memory_gb": 8.0, "storage_gb": 50.0},
            health_check_endpoint="/auth/health",
            recovery_time_objective=60,
            recovery_point_objective=30
        ),
        EdgeService(
            service_id="mumbai_api_gateway",
            service_name="Mumbai API Gateway",
            primary_node="mumbai_backup_01",
            backup_nodes=["mumbai_primary_01", "mumbai_secondary_01"],
            failover_type=FailoverType.LOAD_BALANCING,
            priority=FailoverPriority.HIGH,
            resource_requirements={"cpu_cores": 3, "memory_gb": 12.0, "storage_gb": 75.0},
            health_check_endpoint="/api/health",
            recovery_time_objective=120,
            recovery_point_objective=60
        ),
        EdgeService(
            service_id="mumbai_analytics",
            service_name="Mumbai Analytics Service",
            primary_node="mumbai_secondary_01",
            backup_nodes=["mumbai_emergency_01"],
            failover_type=FailoverType.COLD_STANDBY,
            priority=FailoverPriority.LOW,
            resource_requirements={"cpu_cores": 1, "memory_gb": 4.0, "storage_gb": 200.0},
            health_check_endpoint="/analytics/status",
            recovery_time_objective=300,
            recovery_point_objective=300
        )
    ]
    
    # Register services
    for service in mumbai_services:
        success = failover_manager.register_edge_service(service)
        priority_emoji = {"निम्न": "🟡", "मध्यम": "🟠", "उच्च": "🔴", "गंभीर": "🚨"}
        type_emoji = {"हॉट स्टैंडबाय": "🔥", "वार्म स्टैंडबाय": "🌡️", "कोल्ड स्टैंडबाय": "❄️", "लोड बैलेंसिंग": "⚖️"}
        status_emoji = "✅" if success else "❌"
        
        print(f"{status_emoji} {service.service_name}")
        print(f"   Priority: {priority_emoji[service.priority.value]} | Type: {type_emoji.get(service.failover_type.value, '🔄')}")
        print(f"   Primary: {service.primary_node} | Backups: {len(service.backup_nodes)}")
        print(f"   RTO: {service.recovery_time_objective}s | RPO: {service.recovery_point_objective}s")
    
    # Simulate normal operations
    print(f"\n⚡ Running failover monitoring for 30 seconds...")
    await asyncio.sleep(30)
    
    # Get initial statistics
    initial_stats = failover_manager.get_failover_stats()
    
    print(f"\n📊 Initial System Status:")
    print("-" * 30)
    
    node_stats = initial_stats["node_statistics"]
    service_stats = initial_stats["service_statistics"]
    
    print(f"Nodes: {node_stats['healthy_nodes']}/{node_stats['total_nodes']} healthy")
    print(f"Services: {service_stats['active_services']}/{service_stats['total_services']} active")
    
    # Simulate node failure scenario
    print(f"\n💥 Simulating Primary Node Failure...")
    print("Triggering failure of mumbai_primary_01 (running critical services)")
    
    # Mark primary node as failed
    primary_node = failover_manager.edge_nodes["mumbai_primary_01"]
    await failover_manager._handle_node_failure("mumbai_primary_01", "Simulated hardware failure")
    
    # Wait for failover to complete
    print("⏱️ Waiting for automatic failover...")
    await asyncio.sleep(15)
    
    # Test manual failover
    print(f"\n🔧 Testing Manual Failover...")
    print("Manually failing over Mumbai Analytics Service")
    
    success = await failover_manager.trigger_manual_failover(
        "mumbai_analytics", 
        "mumbai_emergency_01",
        "Manual failover test"
    )
    
    print(f"Manual failover result: {'✅ Success' if success else '❌ Failed'}")
    
    # Wait for recovery monitoring
    print(f"\n🏥 Monitoring service recovery...")
    await asyncio.sleep(20)
    
    # Get final statistics
    final_stats = failover_manager.get_failover_stats()
    
    print(f"\n📊 Final Failover Management Report:")
    print("=" * 50)
    
    # Manager info
    manager_info = final_stats["manager_info"]
    print(f"Manager: {manager_info['manager_id']} @ {manager_info['location']}")
    print(f"Uptime: {manager_info['uptime_hours']} hours")
    print(f"Status: {manager_info['status']}")
    
    # Node statistics
    final_node_stats = final_stats["node_statistics"]
    print(f"\n🖥️ Node Statistics:")
    print(f"• Total Nodes: {final_node_stats['total_nodes']}")
    print(f"• Healthy Nodes: {final_node_stats['healthy_nodes']}")
    print(f"• Failed Nodes: {final_node_stats['failed_nodes']}")
    
    if final_node_stats['node_states']:
        print(f"• Node States:")
        state_emojis = {"स्वस्थ": "🟢", "क्षीण": "🟡", "गंभीर": "🟠", "असफल": "🔴", "रखरखाव": "🔵", "स्टैंडबाय": "⚫"}
        for state, count in final_node_stats['node_states'].items():
            print(f"  {state_emojis.get(state, '🔵')} {state}: {count}")
    
    # Service statistics
    final_service_stats = final_stats["service_statistics"]
    print(f"\n🚀 Service Statistics:")
    print(f"• Total Services: {final_service_stats['total_services']}")
    print(f"• Active Services: {final_service_stats['active_services']}")
    print(f"• Services with Failovers: {final_service_stats['services_with_failovers']}")
    
    # Failover statistics
    failover_stats = final_stats["failover_statistics"]
    print(f"\n🔄 Failover Performance:")
    print(f"• Total Failovers: {failover_stats['total_failovers']}")
    print(f"• Successful: {failover_stats['successful_failovers']}")
    print(f"• Failed: {failover_stats['failed_failovers']}")
    print(f"• Success Rate: {failover_stats['success_rate_percent']:.1f}%")
    print(f"• Avg Failover Time: {failover_stats['avg_failover_time_seconds']:.2f}s")
    print(f"• Avg Recovery Time: {failover_stats['avg_recovery_time_seconds']:.2f}s")
    
    # Recent events
    recent_events = final_stats["recent_events"]
    print(f"\n📋 Recent Events:")
    print(f"• Total Events: {recent_events['total_recent_events']}")
    
    if recent_events['events_by_type']:
        print(f"• Events by Type:")
        for event_type, count in recent_events['events_by_type'].items():
            print(f"  - {event_type.replace('_', ' ').title()}: {count}")
    
    # Display service status after failovers
    print(f"\n🎯 Service Status After Failovers:")
    print("-" * 40)
    
    for service_id, service in failover_manager.edge_services.items():
        original_node = service.primary_node
        current_node = service.current_node
        failover_count = service.failover_count
        
        if current_node != original_node:
            print(f"🔄 {service.service_name}:")
            print(f"   Original: {original_node}")
            print(f"   Current: {current_node}")
            print(f"   Failovers: {failover_count}")
        else:
            print(f"✅ {service.service_name}: Running on original node")
    
    # Cost analysis
    print(f"\n💰 Cost Analysis (Per Incident):")
    print("-" * 30)
    
    incidents_handled = failover_stats['total_failovers']
    edge_failover_cost = incidents_handled * 500   # ₹500 per edge failover
    cloud_failover_cost = incidents_handled * 5000 # ₹5000 per cloud failover
    savings = cloud_failover_cost - edge_failover_cost
    
    print(f"Edge Failover Cost: ₹{edge_failover_cost:,}")
    print(f"Cloud Failover Cost: ₹{cloud_failover_cost:,}")
    print(f"Cost Savings: ₹{savings:,}")
    print(f"Savings Percentage: {(savings/cloud_failover_cost)*100:.1f}%")
    
    # Business benefits
    print(f"\n🎯 Business Benefits:")
    print("• Automated failover reduces downtime")
    print("• High availability for critical services")
    print("• Local backup nodes reduce latency")
    print("• Mumbai-specific disaster recovery")
    print("• Cost-effective compared to cloud failover")
    print("• Real-time monitoring and alerting")
    
    # Mumbai-specific advantages
    print(f"\n🏙️ Mumbai-Specific Advantages:")
    print("• Monsoon-resilient failover strategies")
    print("• Local backup nodes for faster recovery")
    print("• Zone-based failover groups")
    print("• Priority-based service protection")
    print("• Cost optimization for Indian businesses")
    
    # Stop failover manager
    print(f"\n🛑 Stopping failover manager...")
    await failover_manager.stop()
    
    print(f"\n✅ Edge Failover Manager demonstration completed!")
    print(f"🔄 Mumbai railway backup system optimized for high availability!")

if __name__ == "__main__":
    asyncio.run(main())