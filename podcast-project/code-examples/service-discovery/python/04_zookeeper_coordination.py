#!/usr/bin/env python3
"""
🇮🇳 Zookeeper Service Coordination - IRCTC Style
Indian Railway coordination system की तरह distributed coordination

Features:
- Zookeeper-based service coordination
- Leader election for services
- Distributed configuration management
- IRCTC-style train coordination patterns
- Ephemeral nodes for service lifecycle
- Production-ready error handling
- Hindi comments और logging

Author: Agent 5 - Code Developer
Episode: 64 - Service Discovery
Context: IRCTC-style coordination (railway scheduling system)
"""

from kazoo.client import KazooClient, KazooState
from kazoo.recipe.election import Election
from kazoo.recipe.watchers import DataWatch, ChildrenWatch
import json
import time
import threading
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Callable
import logging
import socket
import uuid
from datetime import datetime

# Hindi logging setup - Railway style
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('IRCTCCoordination')

@dataclass
class TrainService:
    """Service registration - IRCTC train service style"""
    service_name: str          # Train name (e.g., "rajdhani-express")
    instance_id: str           # Train number (e.g., "12951-delhi-mumbai")
    host: str                  # Station platform (IP address)
    port: int                  # Platform number (port)
    route: List[str]           # Train route (service endpoints)
    status: str = "SCHEDULED"  # SCHEDULED, RUNNING, DELAYED, CANCELLED
    zone: str = "central"      # Railway zone (region)
    metadata: Dict = None      # Additional train info
    registered_at: float = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.registered_at is None:
            self.registered_at = time.time()

class IRCTCCoordination:
    """
    IRCTC-style service coordination using Zookeeper
    
    Indian Railway analogy:
    - Zookeeper = Railway Control Room
    - Services = Running trains
    - Znodes = Train schedules and status
    - Leader Election = Station Master election
    - Watchers = Real-time train tracking
    - Ephemeral nodes = Train current location
    """
    
    def __init__(self, zk_hosts='localhost:2181', 
                 zone='central-railway', region='western-india'):
        self.zk_hosts = zk_hosts
        self.zone = zone
        self.region = region
        self.zk = None
        self.services = {}  # Local service registry
        self.leaders = {}   # Leader election trackers
        self.watchers = {}  # Service watchers
        self.running = True
        
        # Zookeeper paths (IRCTC style)
        self.base_path = "/irctc"
        self.services_path = f"{self.base_path}/services"
        self.config_path = f"{self.base_path}/config"
        self.leaders_path = f"{self.base_path}/leaders"
        
        self._connect_to_zookeeper()
    
    def _connect_to_zookeeper(self):
        """
        Connect to Zookeeper cluster
        
        Railway control room connection:
        - Establish connection to control center
        - Setup authentication and permissions
        - Initialize required paths
        """
        try:
            self.zk = KazooClient(hosts=self.zk_hosts)
            self.zk.start(timeout=10)
            
            # State change handler
            def connection_listener(state):
                if state == KazooState.LOST:
                    logger.error("🚫 Railway control connection lost!")
                elif state == KazooState.SUSPENDED:
                    logger.warning("⚠️ Railway control connection suspended")
                else:
                    logger.info("✅ Railway control connection restored")
            
            self.zk.add_listener(connection_listener)
            
            # Ensure base paths exist
            self.zk.ensure_path(self.services_path)
            self.zk.ensure_path(self.config_path)
            self.zk.ensure_path(self.leaders_path)
            
            logger.info(f"🚂 IRCTC Coordination connected to {self.zk_hosts}")
            logger.info(f"🏛️ Zone: {self.zone}, Region: {self.region}")
            
        except Exception as e:
            logger.error(f"💥 Zookeeper connection failed: {str(e)}")
            raise
    
    def register_service(self, service: TrainService) -> bool:
        """
        Register a service (train) with coordination system
        
        Train registration process:
        - Register train with control room
        - Set up schedule and route
        - Create ephemeral node for real-time tracking
        - Setup status monitoring
        """
        try:
            service_path = f"{self.services_path}/{service.service_name}"
            instance_path = f"{service_path}/{service.instance_id}"
            
            # Ensure service path exists
            self.zk.ensure_path(service_path)
            
            # Service data
            service_data = {
                "service_name": service.service_name,
                "instance_id": service.instance_id,
                "host": service.host,
                "port": service.port,
                "route": service.route,
                "status": service.status,
                "zone": service.zone,
                "metadata": service.metadata,
                "registered_at": service.registered_at,
                "last_seen": time.time()
            }
            
            # Create ephemeral sequential node
            # यह train के currently running होने का proof है
            actual_path = self.zk.create(
                instance_path,
                json.dumps(service_data).encode('utf-8'),
                ephemeral=True,  # Auto-delete when connection lost
                sequence=False,
                makepath=True
            )
            
            # Store in local registry
            self.services[service.instance_id] = {
                'service': service,
                'zk_path': actual_path
            }
            
            logger.info(f"✅ Train registered: {service.service_name}")
            logger.info(f"🚂 {service.instance_id} scheduled on platform {service.host}:{service.port}")
            logger.info(f"🛤️ Route: {' -> '.join(service.route)}")
            
            # Setup heartbeat
            self._start_service_heartbeat(service)
            
            return True
            
        except Exception as e:
            logger.error(f"💥 Train registration failed: {str(e)}")
            return False
    
    def _start_service_heartbeat(self, service: TrainService):
        """
        Start heartbeat updates for service
        
        Train location updates:
        - Regular status updates to control room
        - Current location and ETA updates
        - Health check responses
        """
        def heartbeat_worker():
            while self.running and service.instance_id in self.services:
                try:
                    service_info = self.services[service.instance_id]
                    zk_path = service_info['zk_path']
                    
                    # Update last_seen timestamp
                    current_data = json.loads(self.zk.get(zk_path)[0].decode('utf-8'))
                    current_data['last_seen'] = time.time()
                    current_data['status'] = service.status
                    
                    # Update in Zookeeper
                    self.zk.set(zk_path, json.dumps(current_data).encode('utf-8'))
                    
                    logger.debug(f"💓 Heartbeat: {service.instance_id}")
                    time.sleep(30)  # 30 second intervals
                    
                except Exception as e:
                    logger.error(f"💥 Heartbeat error for {service.instance_id}: {str(e)}")
                    time.sleep(30)
        
        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=heartbeat_worker)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()
    
    def discover_services(self, service_name: str, 
                         zone: Optional[str] = None) -> List[TrainService]:
        """
        Discover available services (trains)
        
        Train discovery:
        - Find all running trains for a route
        - Filter by zone (railway zone)
        - Return current status and location
        """
        try:
            service_path = f"{self.services_path}/{service_name}"
            
            if not self.zk.exists(service_path):
                logger.info(f"📭 No trains found for route: {service_name}")
                return []
            
            # Get all instances
            children = self.zk.get_children(service_path)
            discovered_services = []
            
            for instance_id in children:
                instance_path = f"{service_path}/{instance_id}"
                
                try:
                    data, stat = self.zk.get(instance_path)
                    service_data = json.loads(data.decode('utf-8'))
                    
                    # Zone filtering
                    if zone and service_data.get('zone') != zone:
                        continue
                    
                    # Check if service is recent (within 2 minutes)
                    last_seen = service_data.get('last_seen', 0)
                    if time.time() - last_seen > 120:
                        logger.warning(f"⚠️ Stale service: {instance_id}")
                        continue
                    
                    # Create TrainService object
                    service = TrainService(
                        service_name=service_data['service_name'],
                        instance_id=service_data['instance_id'],
                        host=service_data['host'],
                        port=service_data['port'],
                        route=service_data['route'],
                        status=service_data['status'],
                        zone=service_data['zone'],
                        metadata=service_data['metadata'],
                        registered_at=service_data['registered_at']
                    )
                    
                    discovered_services.append(service)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Invalid service data for {instance_id}: {str(e)}")
                    continue
            
            logger.info(f"🔍 Found {len(discovered_services)} trains for {service_name}")
            if zone:
                logger.info(f"📍 Filtered by zone: {zone}")
            
            return discovered_services
            
        except Exception as e:
            logger.error(f"💥 Service discovery error: {str(e)}")
            return []
    
    def elect_leader(self, service_name: str, 
                    node_id: str = None) -> Optional[Election]:
        """
        Elect leader for a service group
        
        Station Master election:
        - Multiple services compete for leadership
        - Leader coordinates the service group
        - Automatic failover on leader failure
        """
        try:
            if node_id is None:
                node_id = f"{socket.gethostname()}-{uuid.uuid4().hex[:8]}"
            
            election_path = f"{self.leaders_path}/{service_name}"
            self.zk.ensure_path(election_path)
            
            election = Election(self.zk, election_path, node_id)
            
            def leader_callback():
                logger.info(f"👑 Elected as leader for {service_name}")
                logger.info(f"🏛️ Station Master: {node_id}")
            
            # Start election
            election.run(leader_callback)
            
            self.leaders[service_name] = election
            logger.info(f"🗳️ Joined leadership election for {service_name}")
            
            return election
            
        except Exception as e:
            logger.error(f"💥 Leader election error: {str(e)}")
            return None
    
    def watch_service_changes(self, service_name: str, 
                            callback: Callable[[List[str]], None]):
        """
        Watch for service changes
        
        Train monitoring:
        - Watch for new trains joining route
        - Monitor train departures
        - Real-time status updates
        """
        try:
            service_path = f"{self.services_path}/{service_name}"
            self.zk.ensure_path(service_path)
            
            def watch_callback(children):
                logger.info(f"🔄 Service change detected for {service_name}")
                logger.info(f"🚂 Active trains: {len(children)}")
                
                # Call user callback
                callback(children)
            
            # Setup children watch
            children_watch = ChildrenWatch(self.zk, service_path, watch_callback)
            self.watchers[service_name] = children_watch
            
            logger.info(f"👁️ Watching service: {service_name}")
            return children_watch
            
        except Exception as e:
            logger.error(f"💥 Watch setup error: {str(e)}")
            return None
    
    def set_configuration(self, config_key: str, config_value: Dict) -> bool:
        """
        Set distributed configuration
        
        Railway configuration:
        - Set system-wide configurations
        - Schedule updates and maintenance windows
        - Emergency protocol configurations
        """
        try:
            config_path = f"{self.config_path}/{config_key}"
            config_data = {
                "value": config_value,
                "updated_at": time.time(),
                "updated_by": self.zone
            }
            
            self.zk.ensure_path(self.config_path)
            
            if self.zk.exists(config_path):
                self.zk.set(config_path, json.dumps(config_data).encode('utf-8'))
            else:
                self.zk.create(config_path, json.dumps(config_data).encode('utf-8'))
            
            logger.info(f"⚙️ Configuration updated: {config_key}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Configuration update error: {str(e)}")
            return False
    
    def get_configuration(self, config_key: str) -> Optional[Dict]:
        """Get distributed configuration"""
        try:
            config_path = f"{self.config_path}/{config_key}"
            
            if self.zk.exists(config_path):
                data, stat = self.zk.get(config_path)
                config_data = json.loads(data.decode('utf-8'))
                return config_data.get('value')
            else:
                return None
                
        except Exception as e:
            logger.error(f"💥 Configuration read error: {str(e)}")
            return None
    
    def deregister_service(self, instance_id: str) -> bool:
        """
        Deregister service (train departure)
        
        Train departure process:
        - Remove from active trains list
        - Clean up schedules and resources
        - Notify other services
        """
        try:
            if instance_id not in self.services:
                logger.warning(f"⚠️ Service not found: {instance_id}")
                return False
            
            service_info = self.services[instance_id]
            zk_path = service_info['zk_path']
            
            # Delete from Zookeeper (ephemeral node)
            if self.zk.exists(zk_path):
                self.zk.delete(zk_path)
            
            # Remove from local registry
            del self.services[instance_id]
            
            logger.info(f"✅ Train departed: {instance_id}")
            logger.info(f"🚂 Service deregistered successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"💥 Deregistration error: {str(e)}")
            return False
    
    def get_service_catalog(self) -> Dict[str, List[TrainService]]:
        """
        Get complete service catalog
        
        Railway complete schedule:
        - All running trains
        - All routes and zones
        - Current status and availability
        """
        try:
            if not self.zk.exists(self.services_path):
                return {}
            
            service_names = self.zk.get_children(self.services_path)
            catalog = {}
            
            for service_name in service_names:
                services = self.discover_services(service_name)
                if services:
                    catalog[service_name] = services
            
            logger.info(f"📋 Railway catalog: {len(catalog)} routes available")
            return catalog
            
        except Exception as e:
            logger.error(f"💥 Catalog error: {str(e)}")
            return {}
    
    def shutdown(self):
        """Graceful shutdown"""
        self.running = False
        
        # Stop all leaders
        for service_name, election in self.leaders.items():
            try:
                election.cancel()
            except:
                pass
        
        # Deregister all services
        for instance_id in list(self.services.keys()):
            self.deregister_service(instance_id)
        
        # Close Zookeeper connection
        if self.zk:
            self.zk.stop()
        
        logger.info("🛑 IRCTC Coordination shutdown complete")

# Usage Example
if __name__ == "__main__":
    # Initialize IRCTC coordination
    coordinator = IRCTCCoordination(
        zk_hosts='localhost:2181',
        zone='central-railway',
        region='western-india'
    )
    
    # Define service change callback
    def train_change_handler(train_list):
        print(f"🔄 Train status update: {len(train_list)} active trains")
        for train in train_list:
            print(f"   🚂 {train}")
    
    # Register train services (IRCTC trains)
    trains = [
        TrainService(
            service_name="rajdhani-express",
            instance_id="12951-delhi-mumbai",
            host="10.3.1.10",
            port=8080,
            route=["delhi", "kota", "vadodara", "mumbai"],
            status="RUNNING",
            zone="central-railway",
            metadata={"class": "premium", "speed": "high", "ac": True}
        ),
        TrainService(
            service_name="shatabdi-express", 
            instance_id="12002-delhi-chandigarh",
            host="10.3.1.20",
            port=8081,
            route=["delhi", "ambala", "chandigarh"],
            status="SCHEDULED",
            zone="northern-railway",
            metadata={"class": "premium", "speed": "high", "ac": True}
        ),
        TrainService(
            service_name="mumbai-local",
            instance_id="local-csmt-thane",
            host="10.3.1.30", 
            port=8082,
            route=["csmt", "dadar", "kurla", "thane"],
            status="RUNNING",
            zone="central-railway",
            metadata={"class": "suburban", "frequency": "high", "ac": False}
        )
    ]
    
    # Register all trains
    for train in trains:
        coordinator.register_service(train)
    
    # Setup leader election
    coordinator.elect_leader("rajdhani-express", "station-master-mumbai")
    
    # Setup watchers
    coordinator.watch_service_changes("rajdhani-express", train_change_handler)
    
    # Set configuration
    coordinator.set_configuration("emergency_protocol", {
        "enabled": True,
        "contact": "railway-control@irctc.com",
        "procedures": ["stop_all_trains", "notify_passengers", "emergency_services"]
    })
    
    print("\n🚂 IRCTC Coordination Demo")
    print("=" * 50)
    
    # Service discovery examples
    print("\n1. 🔍 Discovering Rajdhani trains:")
    rajdhani_trains = coordinator.discover_services("rajdhani-express")
    for train in rajdhani_trains:
        print(f"   🚂 {train.instance_id} - Status: {train.status}")
        print(f"      🛤️ Route: {' -> '.join(train.route)}")
    
    print("\n2. 🌍 Zone-specific discovery:")
    central_trains = coordinator.discover_services("mumbai-local", zone="central-railway")
    for train in central_trains:
        print(f"   🚊 {train.instance_id} in {train.zone}")
    
    print("\n3. ⚙️ Getting configuration:")
    emergency_config = coordinator.get_configuration("emergency_protocol")
    if emergency_config:
        print(f"   🚨 Emergency protocol enabled: {emergency_config['enabled']}")
    
    print("\n4. 📋 Complete railway catalog:")
    catalog = coordinator.get_service_catalog()
    for route_name, trains in catalog.items():
        print(f"   🛤️ {route_name}: {len(trains)} trains")
        for train in trains:
            print(f"      📍 {train.zone} - {train.host}:{train.port} ({train.status})")
    
    # Keep running for demo
    try:
        print("\n⏰ Railway system running... (Ctrl+C to stop)")
        print("👁️ Monitoring train movements...")
        time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down railway system...")
        coordinator.shutdown()