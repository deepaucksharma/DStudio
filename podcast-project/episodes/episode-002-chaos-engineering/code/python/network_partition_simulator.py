#!/usr/bin/env python3
"""
Network Partition Simulator - Episode 2
नेटवर्क विभाजन सिमुलेटर

Production-ready network partition simulator for chaos engineering
Chaos engineering के लिए नेटवर्क विभाजन सिमुलेटर

जैसे Mumbai में बारिश के समय कुछ इलाकों का connection कट जाता है -
यह simulate करता है कि services कैसे handle करती हैं network partitions!

Author: Code Developer Agent A5-C-002
Indian Context: Mumbai monsoon network failures, Inter-state connectivity issues
"""

import random
import time
import json
import threading
import socket
import subprocess
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Tuple, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
import asyncio
import ipaddress
from concurrent.futures import ThreadPoolExecutor
import queue
import uuid

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s | समय: %(asctime)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('network_partition.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class PartitionType(Enum):
    """Types of network partitions - नेटवर्क विभाजन के प्रकार"""
    COMPLETE_ISOLATION = "complete_isolation"     # पूर्ण अलगाव - No communication
    ASYMMETRIC = "asymmetric"                     # असममित - A can reach B, but B cannot reach A
    SPLIT_BRAIN = "split_brain"                   # विभाजित मस्तिष्क - Network splits into groups
    INTERMITTENT = "intermittent"                 # रुक-रुक कर - On and off connectivity
    SLOW_NETWORK = "slow_network"                 # धीमा नेटवर्क - High latency, packet loss
    MUMBAI_MONSOON = "mumbai_monsoon"             # मुंबई मानसून - Unpredictable connectivity

class NetworkZone(Enum):
    """Network zones based on Indian geography - भारतीय भूगोल के आधार पर नेटवर्क क्षेत्र"""
    MUMBAI_WEST = "mumbai_west"                   # मुंबई पश्चिम
    MUMBAI_CENTRAL = "mumbai_central"             # मुंबई केंद्रीय
    DELHI_NCR = "delhi_ncr"                       # दिल्ली एनसीआर
    BANGALORE_TECH = "bangalore_tech"             # बैंगलोर तकनीकी
    HYDERABAD_HITEC = "hyderabad_hitec"          # हैदराबाद हाईटेक
    CHENNAI_IT = "chennai_it"                     # चेन्नई आईटी
    PUNE_SOFTWARE = "pune_software"               # पुणे सॉफ्टवेयर
    KOLKATA_FINANCE = "kolkata_finance"           # कोलकाता वित्तीय

@dataclass
class NetworkNode:
    """Represents a network node - एक नेटवर्क नोड का प्रतिनिधित्व"""
    node_id: str
    name: str
    zone: NetworkZone
    ip_address: str
    port: int
    node_type: str  # "web_server", "database", "cache", "load_balancer"
    is_critical: bool = False
    dependencies: List[str] = field(default_factory=list)
    
    # Network characteristics
    base_latency_ms: float = 10.0
    bandwidth_mbps: float = 1000.0
    packet_loss_rate: float = 0.001  # 0.1% packet loss
    
    # Status
    is_reachable: bool = True
    current_connections: Set[str] = field(default_factory=set)
    partition_group: Optional[str] = None

@dataclass
class NetworkLink:
    """Represents a network link between nodes - नोड्स के बीच नेटवर्क लिंक"""
    link_id: str
    source_node: str
    target_node: str
    
    # Link properties
    bandwidth_mbps: float
    latency_ms: float
    packet_loss_rate: float
    is_active: bool = True
    
    # Quality metrics
    congestion_level: float = 0.0  # 0.0 to 1.0
    reliability_score: float = 0.99  # 0.0 to 1.0
    
    # Indian ISP characteristics
    isp_provider: str = "bharti_airtel"  # bharti_airtel, jio, bsnl, etc.
    connection_type: str = "fiber"       # fiber, broadband, mobile, satellite

@dataclass
class PartitionScenario:
    """Defines a network partition scenario - नेटवर्क विभाजन परिदृश्य को परिभाषित करता है"""
    scenario_id: str
    name: str
    partition_type: PartitionType
    affected_zones: List[NetworkZone]
    duration_seconds: int
    
    # Partition parameters
    severity: float = 0.5  # 0.0 to 1.0
    recovery_probability: float = 0.1  # Probability of recovery per check
    
    # Indian context
    monsoon_intensity: str = "moderate"  # light, moderate, heavy, extreme
    power_outage_probability: float = 0.1
    isp_maintenance_window: bool = False
    
    description: str = ""
    expected_impact: str = ""

@dataclass
class PartitionEvent:
    """Records a partition event - विभाजन घटना रिकॉर्ड करता है"""
    event_id: str
    timestamp: datetime
    scenario: PartitionScenario
    affected_nodes: List[str]
    affected_links: List[str]
    
    # Event metrics
    nodes_isolated: int = 0
    connections_lost: int = 0
    service_degradation_score: float = 0.0
    
    # Recovery information
    recovery_time_seconds: Optional[float] = None
    recovery_method: Optional[str] = None
    
    # Impact on services
    critical_services_affected: List[str] = field(default_factory=list)
    user_impact_estimate: int = 0  # Number of users affected

class NetworkPartitionSimulator:
    """Main network partition simulator - मुख्य नेटवर्क विभाजन सिमुलेटर"""
    
    def __init__(self):
        self.nodes: Dict[str, NetworkNode] = {}
        self.links: Dict[str, NetworkLink] = {}
        self.partition_events: List[PartitionEvent] = []
        self.active_partitions: Dict[str, PartitionScenario] = {}
        
        # Network topology
        self.topology_lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Monitoring
        self.is_monitoring = False
        self.monitor_thread = None
        self.metrics_queue = queue.Queue()
        
        # Indian network characteristics
        self.isp_reliability = {
            'bharti_airtel': 0.95,
            'reliance_jio': 0.93,
            'bsnl': 0.85,
            'vodafone_idea': 0.88,
            'tata_communications': 0.97,
            'railwire': 0.82  # Railway WiFi
        }
        
        self.zone_characteristics = {
            NetworkZone.MUMBAI_WEST: {'monsoon_impact': 0.7, 'power_stability': 0.8},
            NetworkZone.MUMBAI_CENTRAL: {'monsoon_impact': 0.6, 'power_stability': 0.85},
            NetworkZone.DELHI_NCR: {'monsoon_impact': 0.3, 'power_stability': 0.75},
            NetworkZone.BANGALORE_TECH: {'monsoon_impact': 0.4, 'power_stability': 0.9},
            NetworkZone.HYDERABAD_HITEC: {'monsoon_impact': 0.35, 'power_stability': 0.88},
            NetworkZone.CHENNAI_IT: {'monsoon_impact': 0.5, 'power_stability': 0.82},
            NetworkZone.PUNE_SOFTWARE: {'monsoon_impact': 0.45, 'power_stability': 0.85},
            NetworkZone.KOLKATA_FINANCE: {'monsoon_impact': 0.6, 'power_stability': 0.78}
        }
        
        logger.info("🌐 Network Partition Simulator initialized | नेटवर्क विभाजन सिमुलेटर शुरू")
    
    def add_node(self, node: NetworkNode):
        """Add a node to the network topology - नेटवर्क टोपोलॉजी में नोड जोड़ें"""
        with self.topology_lock:
            self.nodes[node.node_id] = node
            logger.info(f"📡 Added node: {node.name} ({node.zone.value}) | नोड जोड़ा: {node.name}")
    
    def add_link(self, link: NetworkLink):
        """Add a link between nodes - नोड्स के बीच लिंक जोड़ें"""
        with self.topology_lock:
            self.links[link.link_id] = link
            
            # Update node connections
            if link.source_node in self.nodes:
                self.nodes[link.source_node].current_connections.add(link.target_node)
            if link.target_node in self.nodes:
                self.nodes[link.target_node].current_connections.add(link.source_node)
            
            logger.info(f"🔗 Added link: {link.source_node} ↔ {link.target_node} | लिंक जोड़ा")
    
    def create_indian_network_topology(self):
        """Create a realistic Indian network topology - वास्तविक भारतीय नेटवर्क टोपोलॉजी बनाएं"""
        
        # Create nodes representing major Indian data centers and services
        nodes = [
            # Mumbai nodes
            NetworkNode("mumbai-web-1", "Mumbai Web Server 1", NetworkZone.MUMBAI_WEST, 
                       "10.1.1.10", 80, "web_server", True, ["mumbai-db-1", "mumbai-cache-1"]),
            NetworkNode("mumbai-web-2", "Mumbai Web Server 2", NetworkZone.MUMBAI_CENTRAL, 
                       "10.1.1.11", 80, "web_server", False, ["mumbai-db-1", "mumbai-cache-1"]),
            NetworkNode("mumbai-db-1", "Mumbai Database", NetworkZone.MUMBAI_CENTRAL, 
                       "10.1.2.10", 5432, "database", True, []),
            NetworkNode("mumbai-cache-1", "Mumbai Redis Cache", NetworkZone.MUMBAI_WEST, 
                       "10.1.3.10", 6379, "cache", False, []),
            
            # Delhi nodes
            NetworkNode("delhi-web-1", "Delhi Web Server", NetworkZone.DELHI_NCR, 
                       "10.2.1.10", 80, "web_server", True, ["delhi-db-1"]),
            NetworkNode("delhi-db-1", "Delhi Database", NetworkZone.DELHI_NCR, 
                       "10.2.2.10", 5432, "database", True, []),
            NetworkNode("delhi-lb-1", "Delhi Load Balancer", NetworkZone.DELHI_NCR, 
                       "10.2.4.10", 8080, "load_balancer", True, ["delhi-web-1"]),
            
            # Bangalore nodes
            NetworkNode("blr-api-1", "Bangalore API Server", NetworkZone.BANGALORE_TECH, 
                       "10.3.1.10", 8080, "web_server", True, ["blr-db-1", "blr-cache-1"]),
            NetworkNode("blr-db-1", "Bangalore Database", NetworkZone.BANGALORE_TECH, 
                       "10.3.2.10", 5432, "database", True, []),
            NetworkNode("blr-cache-1", "Bangalore Cache", NetworkZone.BANGALORE_TECH, 
                       "10.3.3.10", 6379, "cache", False, []),
            
            # Hyderabad nodes
            NetworkNode("hyd-analytics-1", "Hyderabad Analytics", NetworkZone.HYDERABAD_HITEC, 
                       "10.4.1.10", 9200, "analytics", False, ["hyd-db-1"]),
            NetworkNode("hyd-db-1", "Hyderabad Database", NetworkZone.HYDERABAD_HITEC, 
                       "10.4.2.10", 5432, "database", False, []),
            
            # Chennai nodes
            NetworkNode("chn-backup-1", "Chennai Backup Server", NetworkZone.CHENNAI_IT, 
                       "10.5.1.10", 8080, "backup", False, []),
        ]
        
        for node in nodes:
            self.add_node(node)
        
        # Create links between nodes
        links = [
            # Mumbai internal links
            NetworkLink("mumbai-web-db", "mumbai-web-1", "mumbai-db-1", 1000.0, 2.0, 0.001, True, 0.1, 0.99, "bharti_airtel", "fiber"),
            NetworkLink("mumbai-web-cache", "mumbai-web-1", "mumbai-cache-1", 1000.0, 1.0, 0.0005, True, 0.05, 0.995, "reliance_jio", "fiber"),
            NetworkLink("mumbai-web2-db", "mumbai-web-2", "mumbai-db-1", 800.0, 3.0, 0.002, True, 0.15, 0.98, "bharti_airtel", "fiber"),
            
            # Inter-city backbone links
            NetworkLink("mumbai-delhi", "mumbai-web-1", "delhi-lb-1", 500.0, 25.0, 0.005, True, 0.3, 0.95, "tata_communications", "fiber"),
            NetworkLink("mumbai-bangalore", "mumbai-web-1", "blr-api-1", 400.0, 35.0, 0.008, True, 0.4, 0.92, "bharti_airtel", "fiber"),
            NetworkLink("delhi-bangalore", "delhi-web-1", "blr-api-1", 300.0, 40.0, 0.01, True, 0.45, 0.90, "reliance_jio", "fiber"),
            NetworkLink("bangalore-hyderabad", "blr-api-1", "hyd-analytics-1", 800.0, 15.0, 0.003, True, 0.2, 0.94, "bharti_airtel", "fiber"),
            NetworkLink("mumbai-chennai", "mumbai-web-1", "chn-backup-1", 200.0, 50.0, 0.015, True, 0.6, 0.88, "bsnl", "fiber"),
            
            # Local connections
            NetworkLink("delhi-internal", "delhi-lb-1", "delhi-web-1", 1000.0, 1.0, 0.0005, True, 0.05, 0.998, "bharti_airtel", "fiber"),
            NetworkLink("blr-api-db", "blr-api-1", "blr-db-1", 1000.0, 2.0, 0.001, True, 0.1, 0.99, "reliance_jio", "fiber"),
            NetworkLink("blr-api-cache", "blr-api-1", "blr-cache-1", 1000.0, 1.0, 0.0005, True, 0.05, 0.995, "bharti_airtel", "fiber"),
        ]
        
        for link in links:
            self.add_link(link)
        
        logger.info(f"🇮🇳 Created Indian network topology: {len(self.nodes)} nodes, {len(self.links)} links")
    
    def create_partition_scenarios(self) -> List[PartitionScenario]:
        """Create realistic partition scenarios - वास्तविक विभाजन परिदृश्य बनाएं"""
        
        scenarios = [
            # Mumbai monsoon scenario
            PartitionScenario(
                scenario_id="mumbai-monsoon-2024",
                name="Mumbai Monsoon Network Failure",
                partition_type=PartitionType.MUMBAI_MONSOON,
                affected_zones=[NetworkZone.MUMBAI_WEST, NetworkZone.MUMBAI_CENTRAL],
                duration_seconds=1800,  # 30 minutes
                severity=0.8,
                recovery_probability=0.05,
                monsoon_intensity="heavy",
                power_outage_probability=0.6,
                description="Heavy monsoon causing power outages and fiber cuts in Mumbai",
                expected_impact="Web services degraded, database connectivity intermittent"
            ),
            
            # Inter-state connectivity issue
            PartitionScenario(
                scenario_id="interstate-fiber-cut",
                name="Interstate Fiber Cable Cut",
                partition_type=PartitionType.COMPLETE_ISOLATION,
                affected_zones=[NetworkZone.BANGALORE_TECH, NetworkZone.HYDERABAD_HITEC],
                duration_seconds=3600,  # 1 hour
                severity=1.0,
                recovery_probability=0.02,
                isp_maintenance_window=False,
                description="Fiber cable cut between Bangalore and Hyderabad",
                expected_impact="Complete isolation of Bangalore-Hyderabad corridor"
            ),
            
            # ISP maintenance split-brain
            PartitionScenario(
                scenario_id="isp-maintenance-split",
                name="ISP Maintenance Split-Brain",
                partition_type=PartitionType.SPLIT_BRAIN,
                affected_zones=[NetworkZone.DELHI_NCR, NetworkZone.PUNE_SOFTWARE],
                duration_seconds=7200,  # 2 hours
                severity=0.6,
                recovery_probability=0.15,
                isp_maintenance_window=True,
                description="Planned ISP maintenance causing split-brain condition",
                expected_impact="Delhi and Pune can't communicate, but each zone internally functional"
            ),
            
            # Asymmetric routing issue
            PartitionScenario(
                scenario_id="asymmetric-routing",
                name="Asymmetric Routing Issue",
                partition_type=PartitionType.ASYMMETRIC,
                affected_zones=[NetworkZone.MUMBAI_CENTRAL, NetworkZone.CHENNAI_IT],
                duration_seconds=900,  # 15 minutes
                severity=0.4,
                recovery_probability=0.3,
                description="Routing table corruption causing asymmetric connectivity",
                expected_impact="Mumbai can reach Chennai, but Chennai cannot reach Mumbai"
            ),
            
            # Intermittent connectivity during festival season
            PartitionScenario(
                scenario_id="festival-overload",
                name="Festival Season Network Overload",
                partition_type=PartitionType.INTERMITTENT,
                affected_zones=[NetworkZone.MUMBAI_WEST, NetworkZone.DELHI_NCR, NetworkZone.BANGALORE_TECH],
                duration_seconds=10800,  # 3 hours
                severity=0.5,
                recovery_probability=0.25,
                description="Festival season causing intermittent network overload",
                expected_impact="Intermittent connectivity across major metros"
            ),
            
            # Slow network due to congestion
            PartitionScenario(
                scenario_id="network-congestion",
                name="Peak Hour Network Congestion",
                partition_type=PartitionType.SLOW_NETWORK,
                affected_zones=[NetworkZone.MUMBAI_WEST, NetworkZone.MUMBAI_CENTRAL],
                duration_seconds=7200,  # 2 hours (peak hours)
                severity=0.3,
                recovery_probability=0.4,
                description="Peak hour network congestion in Mumbai",
                expected_impact="High latency and packet loss, but connections maintained"
            )
        ]
        
        return scenarios
    
    def apply_partition(self, scenario: PartitionScenario) -> PartitionEvent:
        """Apply a network partition scenario - नेटवर्क विभाजन परिदृश्य लागू करें"""
        
        event = PartitionEvent(
            event_id=f"partition_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(),
            scenario=scenario,
            affected_nodes=[],
            affected_links=[]
        )
        
        logger.info(f"🌪️ Applying partition: {scenario.name} | विभाजन लागू कर रहे हैं: {scenario.name}")
        logger.info(f"   Type: {scenario.partition_type.value} | प्रकार: {scenario.partition_type.value}")
        logger.info(f"   Severity: {scenario.severity} | गंभीरता: {scenario.severity}")
        logger.info(f"   Duration: {scenario.duration_seconds}s | अवधि: {scenario.duration_seconds}s")
        
        with self.topology_lock:
            affected_nodes = []
            affected_links = []
            
            # Find nodes in affected zones
            for node_id, node in self.nodes.items():
                if node.zone in scenario.affected_zones:
                    affected_nodes.append(node_id)
                    event.affected_nodes.append(node_id)
                    
                    if node.is_critical:
                        event.critical_services_affected.append(node.name)
            
            # Apply partition based on type
            if scenario.partition_type == PartitionType.COMPLETE_ISOLATION:
                self._apply_complete_isolation(affected_nodes, scenario, event)
                
            elif scenario.partition_type == PartitionType.ASYMMETRIC:
                self._apply_asymmetric_partition(affected_nodes, scenario, event)
                
            elif scenario.partition_type == PartitionType.SPLIT_BRAIN:
                self._apply_split_brain_partition(affected_nodes, scenario, event)
                
            elif scenario.partition_type == PartitionType.INTERMITTENT:
                self._apply_intermittent_partition(affected_nodes, scenario, event)
                
            elif scenario.partition_type == PartitionType.SLOW_NETWORK:
                self._apply_slow_network_partition(affected_nodes, scenario, event)
                
            elif scenario.partition_type == PartitionType.MUMBAI_MONSOON:
                self._apply_mumbai_monsoon_partition(affected_nodes, scenario, event)
            
            # Calculate impact metrics
            event.nodes_isolated = len([n for n in affected_nodes if not self.nodes[n].is_reachable])
            event.connections_lost = len([l for l in self.links.values() if not l.is_active])
            event.service_degradation_score = self._calculate_service_degradation(event)
            event.user_impact_estimate = self._estimate_user_impact(event)
            
            # Store active partition
            self.active_partitions[event.event_id] = scenario
            self.partition_events.append(event)
            
            logger.info(f"📊 Partition applied | विभाजन लागू किया गया:")
            logger.info(f"   Nodes isolated: {event.nodes_isolated} | अलग किए गए नोड्स: {event.nodes_isolated}")
            logger.info(f"   Connections lost: {event.connections_lost} | खोए गए कनेक्शन: {event.connections_lost}")
            logger.info(f"   Service degradation: {event.service_degradation_score:.2f} | सेवा में गिरावट: {event.service_degradation_score:.2f}")
            logger.info(f"   Estimated user impact: {event.user_impact_estimate} | अनुमानित उपयोगकर्ता प्रभाव: {event.user_impact_estimate}")
        
        return event
    
    def _apply_complete_isolation(self, affected_nodes: List[str], scenario: PartitionScenario, event: PartitionEvent):
        """Apply complete isolation - पूर्ण अलगाव लागू करें"""
        
        for node_id in affected_nodes:
            if random.random() < scenario.severity:
                self.nodes[node_id].is_reachable = False
                self.nodes[node_id].partition_group = "isolated"
                logger.debug(f"   🔌 Node {node_id} completely isolated | नोड {node_id} पूर्णतः अलग")
        
        # Disable links involving isolated nodes
        for link_id, link in self.links.items():
            if (link.source_node in affected_nodes or link.target_node in affected_nodes):
                if random.random() < scenario.severity:
                    link.is_active = False
                    event.affected_links.append(link_id)
    
    def _apply_asymmetric_partition(self, affected_nodes: List[str], scenario: PartitionScenario, event: PartitionEvent):
        """Apply asymmetric partition - असममित विभाजन लागू करें"""
        
        # Create asymmetric connectivity - A can reach B, but B cannot reach A
        for link_id, link in self.links.items():
            if link.source_node in affected_nodes or link.target_node in affected_nodes:
                if random.random() < scenario.severity:
                    # Randomly choose direction that works
                    if random.random() < 0.5:
                        # Forward works, reverse doesn't
                        logger.debug(f"   ↗️ Asymmetric: {link.source_node} → {link.target_node} works, reverse fails")
                    else:
                        # Reverse works, forward doesn't
                        logger.debug(f"   ↖️ Asymmetric: {link.target_node} → {link.source_node} works, forward fails")
                    event.affected_links.append(link_id)
    
    def _apply_split_brain_partition(self, affected_nodes: List[str], scenario: PartitionScenario, event: PartitionEvent):
        """Apply split-brain partition - विभाजित मस्तिष्क विभाजन लागू करें"""
        
        # Divide nodes into groups that can't communicate with each other
        if len(affected_nodes) > 1:
            mid_point = len(affected_nodes) // 2
            group_a = affected_nodes[:mid_point]
            group_b = affected_nodes[mid_point:]
            
            for node_id in group_a:
                self.nodes[node_id].partition_group = "group_a"
            
            for node_id in group_b:
                self.nodes[node_id].partition_group = "group_b"
            
            # Disable inter-group links
            for link_id, link in self.links.items():
                source_group = self.nodes.get(link.source_node, {}).partition_group
                target_group = self.nodes.get(link.target_node, {}).partition_group
                
                if (source_group == "group_a" and target_group == "group_b") or \
                   (source_group == "group_b" and target_group == "group_a"):
                    link.is_active = False
                    event.affected_links.append(link_id)
            
            logger.debug(f"   🧠 Split-brain: Group A ({len(group_a)} nodes) ⚡ Group B ({len(group_b)} nodes)")
    
    def _apply_intermittent_partition(self, affected_nodes: List[str], scenario: PartitionScenario, event: PartitionEvent):
        """Apply intermittent partition - रुक-रुक कर विभाजन लागू करें"""
        
        # Intermittent connectivity - connections go on/off
        for node_id in affected_nodes:
            node = self.nodes[node_id]
            # Random intermittent reachability
            node.is_reachable = random.random() > scenario.severity
            node.partition_group = "intermittent"
            
            if not node.is_reachable:
                logger.debug(f"   📶 Node {node_id} temporarily unreachable | नोड अस्थायी रूप से अपहुंच")
        
        # Some links become intermittent
        for link_id, link in self.links.items():
            if link.source_node in affected_nodes or link.target_node in affected_nodes:
                link.is_active = random.random() > scenario.severity
                if not link.is_active:
                    event.affected_links.append(link_id)
    
    def _apply_slow_network_partition(self, affected_nodes: List[str], scenario: PartitionScenario, event: PartitionEvent):
        """Apply slow network partition - धीमे नेटवर्क विभाजन लागू करें"""
        
        # Increase latency and packet loss, but maintain connectivity
        for link_id, link in self.links.items():
            if link.source_node in affected_nodes or link.target_node in affected_nodes:
                # Increase latency by severity factor
                link.latency_ms *= (1 + scenario.severity * 5)  # Up to 5x latency
                
                # Increase packet loss
                link.packet_loss_rate *= (1 + scenario.severity * 10)  # Up to 10x packet loss
                
                # Increase congestion
                link.congestion_level = min(1.0, link.congestion_level + scenario.severity)
                
                event.affected_links.append(link_id)
                logger.debug(f"   🐌 Link {link_id} degraded: latency={link.latency_ms:.1f}ms, loss={link.packet_loss_rate:.3f}")
    
    def _apply_mumbai_monsoon_partition(self, affected_nodes: List[str], scenario: PartitionScenario, event: PartitionEvent):
        """Apply Mumbai monsoon partition - मुंबई मानसून विभाजन लागू करें"""
        
        # Mumbai monsoon causes unpredictable network behavior
        monsoon_effects = {
            'light': {'isolation_prob': 0.1, 'latency_mult': 1.5, 'loss_mult': 2.0},
            'moderate': {'isolation_prob': 0.3, 'latency_mult': 3.0, 'loss_mult': 5.0},
            'heavy': {'isolation_prob': 0.6, 'latency_mult': 6.0, 'loss_mult': 10.0},
            'extreme': {'isolation_prob': 0.9, 'latency_mult': 15.0, 'loss_mult': 50.0}
        }
        
        effects = monsoon_effects[scenario.monsoon_intensity]
        
        for node_id in affected_nodes:
            node = self.nodes[node_id]
            
            # Power outage probability affects node reachability
            if random.random() < scenario.power_outage_probability:
                node.is_reachable = False
                logger.debug(f"   ⚡ Power outage affects node {node_id} | विद्युत कटौती")
            
            # Waterlogging affects ground-level infrastructure
            if node.zone in [NetworkZone.MUMBAI_WEST, NetworkZone.MUMBAI_CENTRAL]:
                if random.random() < effects['isolation_prob']:
                    node.is_reachable = False
                    logger.debug(f"   🌊 Waterlogging isolates node {node_id} | जलभराव")
        
        # Affect inter-zone links more severely
        for link_id, link in self.links.items():
            if any(self.nodes[node_id].zone in scenario.affected_zones 
                   for node_id in [link.source_node, link.target_node] if node_id in self.nodes):
                
                # Monsoon affects fiber cables
                if random.random() < effects['isolation_prob']:
                    link.is_active = False
                    logger.debug(f"   🌧️ Monsoon damages link {link_id} | मानसून से लिंक क्षतिग्रस्त")
                else:
                    # Degraded performance
                    link.latency_ms *= effects['latency_mult']
                    link.packet_loss_rate *= effects['loss_mult']
                    link.congestion_level = min(1.0, effects['isolation_prob'])
                
                event.affected_links.append(link_id)
    
    def _calculate_service_degradation(self, event: PartitionEvent) -> float:
        """Calculate overall service degradation score - समग्र सेवा गिरावट स्कोर की गणना"""
        
        total_score = 0.0
        max_score = 0.0
        
        for node_id in event.affected_nodes:
            node = self.nodes[node_id]
            
            # Weight by criticality
            weight = 10.0 if node.is_critical else 1.0
            max_score += weight
            
            if not node.is_reachable:
                # Completely unreachable
                total_score += weight
            elif node.partition_group == "intermittent":
                # Intermittent issues
                total_score += weight * 0.5
            
        # Add link degradation impact
        degraded_links = len(event.affected_links)
        total_links = len(self.links)
        
        link_impact = (degraded_links / max(total_links, 1)) * 5.0  # Max 5.0 impact from links
        total_score += link_impact
        max_score += 5.0
        
        return min(10.0, (total_score / max(max_score, 1)) * 10.0)  # Scale to 0-10
    
    def _estimate_user_impact(self, event: PartitionEvent) -> int:
        """Estimate number of users affected - प्रभावित उपयोगकर्ताओं की संख्या का अनुमान"""
        
        # Rough estimates based on node types and zones
        zone_populations = {
            NetworkZone.MUMBAI_WEST: 3000000,      # 3M users
            NetworkZone.MUMBAI_CENTRAL: 2500000,   # 2.5M users
            NetworkZone.DELHI_NCR: 5000000,        # 5M users
            NetworkZone.BANGALORE_TECH: 2000000,   # 2M users
            NetworkZone.HYDERABAD_HITEC: 1500000,  # 1.5M users
            NetworkZone.CHENNAI_IT: 1200000,       # 1.2M users
            NetworkZone.PUNE_SOFTWARE: 800000,     # 800K users
            NetworkZone.KOLKATA_FINANCE: 1000000   # 1M users
        }
        
        total_impact = 0
        affected_zones = set()
        
        for node_id in event.affected_nodes:
            if not self.nodes[node_id].is_reachable:
                affected_zones.add(self.nodes[node_id].zone)
        
        for zone in affected_zones:
            population = zone_populations.get(zone, 100000)  # Default 100K
            # Assume severity affects percentage of users impacted
            impact_percentage = event.scenario.severity * 0.3  # Max 30% of zone users
            total_impact += int(population * impact_percentage)
        
        return total_impact
    
    def recover_from_partition(self, event_id: str) -> bool:
        """Recover from a partition - विभाजन से रिकवरी करें"""
        
        if event_id not in self.active_partitions:
            return False
        
        scenario = self.active_partitions[event_id]
        recovery_start = time.time()
        
        logger.info(f"🔧 Starting recovery from partition: {scenario.name} | विभाजन से रिकवरी शुरू")
        
        with self.topology_lock:
            # Find the corresponding event
            event = next((e for e in self.partition_events if e.event_id == event_id), None)
            if not event:
                return False
            
            recovered_nodes = 0
            recovered_links = 0
            
            # Recover nodes
            for node_id in event.affected_nodes:
                if node_id in self.nodes:
                    node = self.nodes[node_id]
                    
                    # Recovery probability check
                    if random.random() < scenario.recovery_probability or scenario.recovery_probability >= 0.5:
                        node.is_reachable = True
                        node.partition_group = None
                        recovered_nodes += 1
                        logger.debug(f"   ✅ Node {node_id} recovered | नोड रिकवर हुआ")
            
            # Recover links
            for link_id in event.affected_links:
                if link_id in self.links:
                    link = self.links[link_id]
                    
                    if random.random() < scenario.recovery_probability or scenario.recovery_probability >= 0.5:
                        link.is_active = True
                        
                        # Reset degraded parameters for slow network partitions
                        if scenario.partition_type == PartitionType.SLOW_NETWORK:
                            link.latency_ms = link.latency_ms / (1 + scenario.severity * 5)
                            link.packet_loss_rate = link.packet_loss_rate / (1 + scenario.severity * 10)
                            link.congestion_level = max(0.0, link.congestion_level - scenario.severity)
                        
                        recovered_links += 1
                        logger.debug(f"   🔗 Link {link_id} recovered | लिंक रिकवर हुआ")
            
            # Update event with recovery information
            event.recovery_time_seconds = time.time() - recovery_start
            event.recovery_method = "automatic_recovery"
            
            # Remove from active partitions if fully recovered
            if recovered_nodes == len(event.affected_nodes) and recovered_links == len(event.affected_links):
                del self.active_partitions[event_id]
                logger.info(f"✅ Full recovery completed for {scenario.name} | पूर्ण रिकवरी पूर्ण")
                return True
            else:
                logger.info(f"🔄 Partial recovery: {recovered_nodes}/{len(event.affected_nodes)} nodes, " +
                           f"{recovered_links}/{len(event.affected_links)} links | आंशिक रिकवरी")
        
        return False
    
    def get_network_status(self) -> Dict[str, Any]:
        """Get current network status - वर्तमान नेटवर्क स्थिति प्राप्त करें"""
        
        with self.topology_lock:
            reachable_nodes = sum(1 for node in self.nodes.values() if node.is_reachable)
            active_links = sum(1 for link in self.links.values() if link.is_active)
            
            critical_nodes_down = sum(1 for node in self.nodes.values() 
                                    if node.is_critical and not node.is_reachable)
            
            partition_groups = {}
            for node in self.nodes.values():
                if node.partition_group:
                    partition_groups[node.partition_group] = partition_groups.get(node.partition_group, 0) + 1
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total_nodes': len(self.nodes),
                'reachable_nodes': reachable_nodes,
                'unreachable_nodes': len(self.nodes) - reachable_nodes,
                'total_links': len(self.links),
                'active_links': active_links,
                'inactive_links': len(self.links) - active_links,
                'critical_nodes_down': critical_nodes_down,
                'active_partitions': len(self.active_partitions),
                'partition_groups': partition_groups,
                'network_health_percentage': (reachable_nodes / max(len(self.nodes), 1)) * 100,
                'connectivity_percentage': (active_links / max(len(self.links), 1)) * 100
            }
    
    def generate_network_report(self) -> Dict[str, Any]:
        """Generate comprehensive network report - व्यापक नेटवर्क रिपोर्ट जेनरेट करें"""
        
        current_status = self.get_network_status()
        
        # Event statistics
        total_events = len(self.partition_events)
        events_by_type = {}
        total_downtime = 0
        total_users_affected = 0
        
        for event in self.partition_events:
            event_type = event.scenario.partition_type.value
            events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
            
            if event.recovery_time_seconds:
                total_downtime += event.recovery_time_seconds
            
            total_users_affected += event.user_impact_estimate
        
        # Zone impact analysis
        zone_impact = {}
        for event in self.partition_events:
            for zone in event.scenario.affected_zones:
                zone_name = zone.value
                zone_impact[zone_name] = zone_impact.get(zone_name, 0) + 1
        
        # ISP reliability analysis
        isp_analysis = {}
        for link in self.links.values():
            isp = link.isp_provider
            if isp not in isp_analysis:
                isp_analysis[isp] = {'total_links': 0, 'active_links': 0, 'reliability': 0}
            
            isp_analysis[isp]['total_links'] += 1
            if link.is_active:
                isp_analysis[isp]['active_links'] += 1
        
        for isp, data in isp_analysis.items():
            if data['total_links'] > 0:
                data['reliability'] = (data['active_links'] / data['total_links']) * 100
        
        return {
            'report_generated_at': datetime.now().isoformat(),
            'current_status': current_status,
            'historical_analysis': {
                'total_partition_events': total_events,
                'events_by_type': events_by_type,
                'total_downtime_seconds': total_downtime,
                'average_event_duration': total_downtime / max(total_events, 1),
                'total_users_affected': total_users_affected,
                'average_users_per_event': total_users_affected / max(total_events, 1)
            },
            'zone_impact_analysis': zone_impact,
            'isp_reliability_analysis': isp_analysis,
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on network analysis - नेटवर्क विश्लेषण के आधार पर सिफारिशें जेनरेट करें"""
        
        recommendations = []
        
        # Analyze partition patterns
        monsoon_events = len([e for e in self.partition_events 
                            if e.scenario.partition_type == PartitionType.MUMBAI_MONSOON])
        
        if monsoon_events > 2:
            recommendations.append(
                "मुंबई में मानसून-प्रूफ इंफ्रास्ट्रक्चर में निवेश करें - बार बार मानसून की समस्या"
            )
        
        # Check critical node failures
        critical_failures = len([e for e in self.partition_events 
                               if any(self.nodes.get(node_id, {}).is_critical 
                                     for node_id in e.affected_nodes)])
        
        if critical_failures > 1:
            recommendations.append(
                "Critical services के लिए redundancy बढ़ाएं - अधिक failures हो रहे हैं"
            )
        
        # Analyze ISP diversity
        active_isps = set(link.isp_provider for link in self.links.values() if link.is_active)
        if len(active_isps) < 3:
            recommendations.append(
                "ISP diversity बढ़ाएं - कम से कम 3-4 ISPs का उपयोग करें"
            )
        
        # Check inter-zone connectivity
        split_brain_events = len([e for e in self.partition_events 
                                if e.scenario.partition_type == PartitionType.SPLIT_BRAIN])
        
        if split_brain_events > 1:
            recommendations.append(
                "Inter-zone में अधिक redundant links जोड़ें - split-brain की समस्या"
            )
        
        # Default recommendations
        if not recommendations:
            recommendations.extend([
                "नेटवर्क resilience अच्छी है - वर्तमान architecture बनाए रखें",
                "Regular chaos engineering tests चलाते रहें",
                "Monitoring और alerting systems को enhance करें"
            ])
        
        return recommendations

def main():
    """Main function to demonstrate network partition simulator - मुख्य function"""
    
    print("🌐 Network Partition Simulator Demo - Episode 2")
    print("नेटवर्क विभाजन सिमुलेटर डेमो - एपिसोड 2\n")
    
    # Create simulator and setup network
    simulator = NetworkPartitionSimulator()
    
    # Create Indian network topology
    simulator.create_indian_network_topology()
    
    # Show initial network status
    print("📊 Initial Network Status:")
    initial_status = simulator.get_network_status()
    print(f"   Nodes: {initial_status['total_nodes']}")
    print(f"   Links: {initial_status['total_links']}")
    print(f"   Network Health: {initial_status['network_health_percentage']:.1f}%")
    print(f"   Connectivity: {initial_status['connectivity_percentage']:.1f}%")
    
    # Create and run partition scenarios
    scenarios = simulator.create_partition_scenarios()
    
    print(f"\n{'='*80}")
    print("RUNNING PARTITION SCENARIOS | विभाजन परिदृश्य चला रहे हैं")
    print('='*80)
    
    active_events = []
    
    # Apply a few scenarios
    scenarios_to_run = scenarios[:3]  # Run first 3 scenarios
    
    for i, scenario in enumerate(scenarios_to_run, 1):
        print(f"\n🌪️ SCENARIO {i}: {scenario.name}")
        print(f"परिदृश्य {i}: {scenario.name}")
        print("-" * 50)
        
        # Apply partition
        event = simulator.apply_partition(scenario)
        active_events.append(event)
        
        # Show immediate impact
        current_status = simulator.get_network_status()
        print(f"   Network Health: {initial_status['network_health_percentage']:.1f}% → {current_status['network_health_percentage']:.1f}%")
        print(f"   Critical Services Down: {current_status['critical_nodes_down']}")
        print(f"   Active Partitions: {current_status['active_partitions']}")
        
        # Wait a bit before next scenario
        if i < len(scenarios_to_run):
            print(f"   Waiting 5 seconds before next scenario...")
            time.sleep(5)
    
    # Show combined impact
    print(f"\n{'='*80}")
    print("COMBINED IMPACT ANALYSIS | संयुक्त प्रभाव विश्लेषण")
    print('='*80)
    
    combined_status = simulator.get_network_status()
    print(f"Total Network Degradation:")
    print(f"   Reachable Nodes: {combined_status['reachable_nodes']}/{combined_status['total_nodes']}")
    print(f"   Active Links: {combined_status['active_links']}/{combined_status['total_links']}")
    print(f"   Network Health: {combined_status['network_health_percentage']:.1f}%")
    print(f"   Active Partitions: {combined_status['active_partitions']}")
    
    if combined_status['partition_groups']:
        print(f"   Partition Groups:")
        for group, count in combined_status['partition_groups'].items():
            print(f"     {group}: {count} nodes")
    
    # Demonstrate recovery
    print(f"\n{'='*80}")
    print("RECOVERY SIMULATION | रिकवरी सिमुलेशन")
    print('='*80)
    
    print("Attempting recovery from partitions...")
    print("विभाजनों से रिकवरी का प्रयास...")
    
    recovered_events = 0
    for event in active_events:
        print(f"\n🔧 Recovering from: {event.scenario.name}")
        
        # Increase recovery probability for demo
        event.scenario.recovery_probability = 0.8  # 80% recovery chance
        
        if simulator.recover_from_partition(event.event_id):
            print(f"   ✅ Recovery successful | रिकवरी सफल")
            recovered_events += 1
        else:
            print(f"   ⏳ Partial recovery | आंशिक रिकवरी")
    
    # Show final status
    final_status = simulator.get_network_status()
    print(f"\nFinal Network Status after recovery attempts:")
    print(f"   Network Health: {final_status['network_health_percentage']:.1f}%")
    print(f"   Connectivity: {final_status['connectivity_percentage']:.1f}%")
    print(f"   Recovered Events: {recovered_events}/{len(active_events)}")
    
    # Generate comprehensive report
    print(f"\n{'='*80}")
    print("COMPREHENSIVE NETWORK REPORT | व्यापक नेटवर्क रिपोर्ट")
    print('='*80)
    
    report = simulator.generate_network_report()
    
    # Show key metrics
    historical = report['historical_analysis']
    print(f"Historical Analysis:")
    print(f"   Total Partition Events: {historical['total_partition_events']}")
    print(f"   Total Downtime: {historical['total_downtime_seconds']:.1f}s")
    print(f"   Average Event Duration: {historical['average_event_duration']:.1f}s")
    print(f"   Total Users Affected: {historical['total_users_affected']:,}")
    
    # Events by type
    print(f"\nEvents by Type:")
    for event_type, count in historical['events_by_type'].items():
        print(f"   {event_type}: {count}")
    
    # Zone impact
    print(f"\nZone Impact Analysis:")
    for zone, impact in report['zone_impact_analysis'].items():
        print(f"   {zone}: {impact} events")
    
    # ISP reliability
    print(f"\nISP Reliability Analysis:")
    for isp, data in report['isp_reliability_analysis'].items():
        print(f"   {isp}: {data['reliability']:.1f}% ({data['active_links']}/{data['total_links']} links)")
    
    # Recommendations
    print(f"\nRecommendations | सिफारिशें:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"   {i}. {rec}")
    
    # Save report to file
    report_filename = f"network_partition_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📁 Detailed report saved: {report_filename}")
    
    print(f"\n🎉 Network Partition Simulator demonstration completed!")
    print("नेटवर्क विभाजन सिमुलेटर प्रदर्शन पूर्ण!")
    
    print(f"\n💡 KEY LEARNINGS | मुख्य शिक्षाएं:")
    print("1. Network partitions are inevitable - design for resilience")
    print("   नेटवर्क विभाजन अपरिहार्य हैं - resilience के लिए design करें")
    print("2. Mumbai monsoon significantly impacts network infrastructure")
    print("   मुंबई मानसून नेटवर्क infrastructure को काफी प्रभावित करता है")
    print("3. ISP diversity is crucial for fault tolerance")
    print("   Fault tolerance के लिए ISP diversity महत्वपूर्ण है")
    print("4. Critical services need redundancy across zones")
    print("   Critical services को zones में redundancy चाहिए")

if __name__ == "__main__":
    main()