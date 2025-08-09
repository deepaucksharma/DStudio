# Episode 108: Network Topology Design - Part 2: Implementation Details

## Episode Overview

Welcome to Part 2 of our comprehensive exploration of Network Topology Design. While Part 1 covered the theoretical foundations and design principles, this episode dives deep into the practical implementation details that transform network designs into production-ready distributed systems. Over the next two hours, we'll explore VLAN and VXLAN configurations, routing protocol implementations, software-defined networking integration, network virtualization overlays, and automation strategies that modern enterprises rely on.

## Segment 1: VLAN and VXLAN Implementation (45 minutes)

### Virtual LAN (VLAN) Deep Implementation

Virtual LANs represent one of the fundamental building blocks of modern network segmentation. Understanding their implementation is crucial for anyone designing scalable network topologies.

#### Core VLAN Configuration Principles

VLANs operate at Layer 2 of the OSI model, creating logical broadcast domains within a physical network infrastructure. The IEEE 802.1Q standard defines how VLAN tags are inserted into Ethernet frames, adding a 4-byte header that includes a 12-bit VLAN ID field, supporting up to 4,094 VLANs per switch.

```python
# Example VLAN configuration parser for network automation
class VLANConfig:
    def __init__(self, vlan_id, name, description=""):
        if not (1 <= vlan_id <= 4094):
            raise ValueError("VLAN ID must be between 1 and 4094")
        self.vlan_id = vlan_id
        self.name = name
        self.description = description
        self.ports = []
        self.trunk_ports = []
    
    def add_access_port(self, port_id):
        """Add an access port to this VLAN"""
        self.ports.append({
            'port_id': port_id,
            'type': 'access',
            'allowed_vlans': [self.vlan_id]
        })
    
    def add_trunk_port(self, port_id, allowed_vlans=None):
        """Add a trunk port with multiple VLANs"""
        if allowed_vlans is None:
            allowed_vlans = [self.vlan_id]
        self.trunk_ports.append({
            'port_id': port_id,
            'type': 'trunk',
            'allowed_vlans': allowed_vlans
        })
    
    def generate_cisco_config(self):
        """Generate Cisco switch configuration"""
        config = [f"vlan {self.vlan_id}"]
        config.append(f" name {self.name}")
        if self.description:
            config.append(f" description {self.description}")
        config.append("!")
        
        # Configure access ports
        for port in self.ports:
            config.extend([
                f"interface {port['port_id']}",
                " switchport mode access",
                f" switchport access vlan {self.vlan_id}",
                "!"
            ])
        
        # Configure trunk ports
        for port in self.trunk_ports:
            vlan_list = ",".join(map(str, port['allowed_vlans']))
            config.extend([
                f"interface {port['port_id']}",
                " switchport mode trunk",
                f" switchport trunk allowed vlan {vlan_list}",
                "!"
            ])
        
        return "\n".join(config)
```

#### Advanced VLAN Scenarios

Modern enterprises often implement complex VLAN strategies that require careful planning:

**Voice and Data Segregation**: In enterprise environments, separating voice traffic from data traffic improves quality of service and security. This typically involves configuring voice VLANs (often VLAN 150-199 range) with appropriate QoS markings.

**Guest Network Isolation**: Guest networks require complete isolation from corporate resources while maintaining internet access. This involves VLAN segmentation combined with firewall rules and captive portal authentication.

**Multi-tenant Environments**: Cloud providers and managed service providers use VLANs to create tenant isolation. Each tenant gets dedicated VLANs, ensuring complete traffic separation at Layer 2.

#### VLAN Spanning Tree Protocol (STP) Considerations

When implementing VLANs across multiple switches, Spanning Tree Protocol becomes critical. Per-VLAN Spanning Tree Plus (PVST+) and Multiple Spanning Tree Protocol (MSTP) offer different approaches:

```python
class SpanningTreeConfig:
    def __init__(self, mode='pvst+'):
        self.mode = mode
        self.root_bridges = {}
        self.port_costs = {}
        self.port_priorities = {}
    
    def set_root_bridge(self, vlan_id, bridge_priority=8192):
        """Configure root bridge for specific VLAN"""
        self.root_bridges[vlan_id] = bridge_priority
    
    def optimize_convergence(self, enable_portfast=True, enable_bpduguard=True):
        """Enable STP optimizations for faster convergence"""
        optimizations = []
        if enable_portfast:
            optimizations.append("spanning-tree portfast default")
        if enable_bpduguard:
            optimizations.append("spanning-tree portfast bpduguard default")
        return optimizations
    
    def generate_config(self, vlan_list):
        config = [f"spanning-tree mode {self.mode}"]
        
        for vlan_id in vlan_list:
            if vlan_id in self.root_bridges:
                priority = self.root_bridges[vlan_id]
                config.append(f"spanning-tree vlan {vlan_id} priority {priority}")
        
        config.extend(self.optimize_convergence())
        return "\n".join(config)
```

### VXLAN Implementation Deep Dive

Virtual Extensible LAN (VXLAN) addresses the scalability limitations of traditional VLANs by providing Layer 2 connectivity over Layer 3 networks. VXLAN uses a 24-bit segment ID, supporting over 16 million logical networks compared to VLAN's 4,094 limit.

#### VXLAN Architecture Components

VXLAN operates through several key components:

**VTEP (VXLAN Tunnel Endpoint)**: Physical or virtual switches that perform VXLAN encapsulation and decapsulation. VTEPs maintain mapping tables between MAC addresses and remote VTEP IP addresses.

**VNI (VXLAN Network Identifier)**: The 24-bit identifier that uniquely identifies a VXLAN segment, similar to a VLAN ID but with much larger address space.

**VXLAN Gateway**: Provides connectivity between VXLAN and non-VXLAN domains, handling protocol translation and routing.

#### Practical VXLAN Configuration

Here's a comprehensive example of VXLAN implementation using modern network automation:

```python
import ipaddress
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class VTEPConfig:
    vtep_ip: str
    loopback_ip: str
    vni_mappings: Dict[int, str]  # VNI to VLAN mapping
    
    def validate_config(self):
        """Validate VTEP configuration"""
        try:
            ipaddress.ip_address(self.vtep_ip)
            ipaddress.ip_address(self.loopback_ip)
        except ipaddress.AddressValueError as e:
            raise ValueError(f"Invalid IP address: {e}")
        
        for vni in self.vni_mappings.keys():
            if not (1 <= vni <= 16777215):
                raise ValueError(f"VNI {vni} out of range (1-16777215)")

class VXLANNetworkManager:
    def __init__(self):
        self.vteps: List[VTEPConfig] = []
        self.vni_registry: Dict[int, str] = {}
        self.multicast_groups: Dict[int, str] = {}
    
    def add_vtep(self, vtep_config: VTEPConfig):
        """Add VTEP to the network"""
        vtep_config.validate_config()
        self.vteps.append(vtep_config)
    
    def configure_vni(self, vni: int, description: str, multicast_group: str = None):
        """Configure VNI with optional multicast group"""
        if multicast_group:
            # Validate multicast address (224.0.0.0 to 239.255.255.255)
            mc_addr = ipaddress.ip_address(multicast_group)
            if not mc_addr.is_multicast:
                raise ValueError("Invalid multicast address")
            self.multicast_groups[vni] = multicast_group
        
        self.vni_registry[vni] = description
    
    def generate_cisco_nxos_config(self, vtep: VTEPConfig):
        """Generate Cisco NX-OS VXLAN configuration"""
        config = [
            "feature vn-segment-vlan-based",
            "feature nv overlay",
            "feature vxlan",
            "",
            f"interface loopback0",
            f" ip address {vtep.loopback_ip}/32",
            " ip pim sparse-mode",
            "",
            f"interface nve1",
            " no shutdown",
            f" source-interface loopback0"
        ]
        
        # Configure VNI mappings
        for vni, vlan in vtep.vni_mappings.items():
            config.append(f" member vni {vni}")
            if vni in self.multicast_groups:
                config.append(f"  multicast-group {self.multicast_groups[vni]}")
        
        config.extend(["", "# VLAN to VNI mappings"])
        for vni, vlan in vtep.vni_mappings.items():
            config.extend([
                f"vlan {vlan}",
                f" vn-segment {vni}"
            ])
        
        return "\n".join(config)
    
    def generate_evpn_config(self, as_number: int, router_id: str):
        """Generate EVPN BGP configuration for VXLAN"""
        config = [
            f"router bgp {as_number}",
            f" router-id {router_id}",
            " address-family l2vpn evpn",
            "  retain route-target all",
            "",
            " template peer-policy EVPN_POLICY",
            "  send-community extended",
            "  route-reflector-client",
            " template peer-session EVPN_SESSION",
            "  remote-as " + str(as_number),
            "  update-source loopback0"
        ]
        return "\n".join(config)

# Example usage
vxlan_manager = VXLANNetworkManager()

# Configure VNIs
vxlan_manager.configure_vni(10100, "Web_Tier", "239.1.1.100")
vxlan_manager.configure_vni(10200, "App_Tier", "239.1.1.200")
vxlan_manager.configure_vni(10300, "DB_Tier", "239.1.1.300")

# Configure VTEPs
vtep1 = VTEPConfig(
    vtep_ip="10.1.1.10",
    loopback_ip="10.255.1.1",
    vni_mappings={10100: "100", 10200: "200", 10300: "300"}
)

vxlan_manager.add_vtep(vtep1)
print(vxlan_manager.generate_cisco_nxos_config(vtep1))
```

#### VXLAN with EVPN Control Plane

Ethernet VPN (EVPN) provides a robust control plane for VXLAN, eliminating the need for multicast in the underlay network and providing advanced features like multi-homing and optimized traffic forwarding.

```python
class EVPNVXLANController:
    def __init__(self, bgp_as: int):
        self.bgp_as = bgp_as
        self.route_targets = {}
        self.route_distinguishers = {}
        self.vni_mappings = {}
    
    def configure_l2vni(self, vni: int, rd: str, rt_import: str, rt_export: str):
        """Configure Layer 2 VNI with EVPN parameters"""
        self.route_distinguishers[vni] = rd
        self.route_targets[vni] = {
            'import': rt_import,
            'export': rt_export
        }
    
    def configure_l3vni(self, vni: int, vrf_name: str, rd: str, rt: str):
        """Configure Layer 3 VNI for inter-subnet routing"""
        self.vni_mappings[vni] = {
            'type': 'l3',
            'vrf': vrf_name,
            'rd': rd,
            'rt': rt
        }
    
    def generate_evpn_instance_config(self, vni: int):
        """Generate EVPN instance configuration"""
        if vni not in self.route_distinguishers:
            raise ValueError(f"VNI {vni} not configured")
        
        config = [
            f"evpn instance {vni} vlan {vni}",
            f" rd {self.route_distinguishers[vni]}",
            f" route-target import {self.route_targets[vni]['import']}",
            f" route-target export {self.route_targets[vni]['export']}"
        ]
        return "\n".join(config)
```

## Segment 2: BGP and OSPF Configuration for Different Topologies (50 minutes)

### Border Gateway Protocol (BGP) Implementation

BGP serves as the routing foundation for both internet connectivity and large-scale data center networks. Modern implementations leverage BGP for both external connectivity (eBGP) and internal routing (iBGP), particularly in spine-leaf architectures.

#### BGP Fundamentals in Data Center Design

Data center networks have evolved from traditional hierarchical designs to more scalable spine-leaf topologies. This evolution has driven new BGP implementation patterns:

```python
import ipaddress
from enum import Enum
from typing import Dict, List, Set

class BGPSessionType(Enum):
    EBGP = "external"
    IBGP = "internal"
    CONFEDERATION = "confederation"

class BGPNeighbor:
    def __init__(self, neighbor_ip: str, remote_as: int, session_type: BGPSessionType):
        self.neighbor_ip = ipaddress.ip_address(neighbor_ip)
        self.remote_as = remote_as
        self.session_type = session_type
        self.address_families = set()
        self.route_maps = {}
        self.timers = {'keepalive': 60, 'holdtime': 180}
        self.authentication = None
    
    def add_address_family(self, af_type: str, policies: Dict = None):
        """Add address family configuration"""
        self.address_families.add(af_type)
        if policies:
            self.route_maps[af_type] = policies
    
    def set_timers(self, keepalive: int, holdtime: int):
        """Configure BGP timers"""
        if holdtime < 3 * keepalive:
            raise ValueError("Holdtime must be at least 3 times keepalive")
        self.timers = {'keepalive': keepalive, 'holdtime': holdtime}

class DataCenterBGPConfig:
    def __init__(self, local_as: int, router_id: str):
        self.local_as = local_as
        self.router_id = router_id
        self.neighbors: List[BGPNeighbor] = []
        self.networks = set()
        self.aggregate_addresses = []
        self.route_reflector_clients = set()
    
    def add_spine_leaf_neighbors(self, spine_ips: List[str], leaf_as_base: int):
        """Configure BGP for spine-leaf topology"""
        for i, spine_ip in enumerate(spine_ips):
            # In spine-leaf, each spine typically has its own AS
            spine_as = leaf_as_base + 100 + i
            neighbor = BGPNeighbor(spine_ip, spine_as, BGPSessionType.EBGP)
            neighbor.add_address_family("ipv4_unicast")
            neighbor.add_address_family("l2vpn_evpn")
            self.neighbors.append(neighbor)
    
    def configure_route_reflector(self, client_ips: List[str]):
        """Configure BGP route reflector for iBGP scaling"""
        for client_ip in client_ips:
            self.route_reflector_clients.add(client_ip)
            neighbor = BGPNeighbor(client_ip, self.local_as, BGPSessionType.IBGP)
            neighbor.add_address_family("ipv4_unicast")
            neighbor.add_address_family("vpnv4_unicast")
            self.neighbors.append(neighbor)
    
    def generate_cisco_config(self):
        """Generate Cisco BGP configuration"""
        config = [
            f"router bgp {self.local_as}",
            f" bgp router-id {self.router_id}",
            " bgp log-neighbor-changes",
            " no bgp default ipv4-unicast"
        ]
        
        # Configure neighbors
        for neighbor in self.neighbors:
            config.extend([
                f" neighbor {neighbor.neighbor_ip} remote-as {neighbor.remote_as}",
                f" neighbor {neighbor.neighbor_ip} timers {neighbor.timers['keepalive']} {neighbor.timers['holdtime']}"
            ])
            
            if neighbor.session_type == BGPSessionType.IBGP:
                config.append(f" neighbor {neighbor.neighbor_ip} update-source loopback0")
                if str(neighbor.neighbor_ip) in self.route_reflector_clients:
                    config.append(f" neighbor {neighbor.neighbor_ip} route-reflector-client")
        
        # Configure address families
        for af in set().union(*[n.address_families for n in self.neighbors]):
            config.append(f" address-family {af.replace('_', ' ')}")
            for neighbor in self.neighbors:
                if af in neighbor.address_families:
                    config.append(f"  neighbor {neighbor.neighbor_ip} activate")
                    if af in neighbor.route_maps:
                        for direction, policy in neighbor.route_maps[af].items():
                            config.append(f"  neighbor {neighbor.neighbor_ip} route-map {policy} {direction}")
            config.append(" exit-address-family")
        
        return "\n".join(config)
    
    def optimize_for_fast_convergence(self):
        """Apply BGP optimizations for fast convergence"""
        optimizations = [
            " bgp fast-external-fallover",
            " bgp bestpath as-path multipath-relax",
            " maximum-paths 64",  # Enable ECMP
            " bgp additional-paths send receive",  # BGP Add-Paths
            " bgp bestpath compare-routerid"
        ]
        return optimizations

# Example: Spine-Leaf BGP Configuration
leaf_switch = DataCenterBGPConfig(local_as=65001, router_id="10.255.1.1")
spine_ips = ["10.1.1.1", "10.1.1.2", "10.1.1.3", "10.1.1.4"]
leaf_switch.add_spine_leaf_neighbors(spine_ips, leaf_as_base=65000)

print("=== Leaf Switch BGP Configuration ===")
print(leaf_switch.generate_cisco_config())
```

#### Advanced BGP Features for Data Centers

Modern data center BGP implementations leverage several advanced features:

**BGP EVPN for VXLAN**: EVPN provides a control plane for VXLAN overlays, advertising MAC/IP information through BGP.

```python
class BGPEVPNConfig:
    def __init__(self, bgp_config: DataCenterBGPConfig):
        self.bgp_config = bgp_config
        self.vni_mappings = {}
        self.anycast_gateways = {}
    
    def configure_l2vni_evpn(self, vni: int, rd: str, rt: str):
        """Configure EVPN for Layer 2 VNI"""
        self.vni_mappings[vni] = {
            'type': 'l2',
            'rd': rd,
            'rt': rt
        }
    
    def configure_anycast_gateway(self, vlan_id: int, gateway_ip: str, mac: str):
        """Configure anycast gateway for distributed routing"""
        self.anycast_gateways[vlan_id] = {
            'ip': gateway_ip,
            'mac': mac
        }
    
    def generate_evpn_config(self):
        """Generate EVPN-specific configuration"""
        config = []
        
        for vni, mapping in self.vni_mappings.items():
            config.extend([
                f"evpn instance {vni} vlan {vni}",
                f" rd {mapping['rd']}",
                f" route-target import {mapping['rt']}",
                f" route-target export {mapping['rt']}"
            ])
        
        # Anycast gateway configuration
        for vlan, gateway in self.anycast_gateways.items():
            config.extend([
                f"interface vlan{vlan}",
                f" ip address {gateway['ip']}",
                " fabric forwarding mode anycast-gateway"
            ])
        
        # Global anycast gateway MAC
        if self.anycast_gateways:
            first_mac = list(self.anycast_gateways.values())[0]['mac']
            config.insert(0, f"fabric forwarding anycast-gateway-mac {first_mac}")
        
        return "\n".join(config)
```

### OSPF Implementation Strategies

Open Shortest Path First (OSPF) remains critical for intra-domain routing, particularly in campus networks and enterprise WANs. Modern OSPF implementations focus on scalability and convergence optimization.

#### OSPF Area Design and Implementation

Proper OSPF area design is crucial for scalability and performance:

```python
from dataclasses import dataclass
from typing import List, Dict, Set
import ipaddress

@dataclass
class OSPFArea:
    area_id: str
    area_type: str = "normal"  # normal, stub, totally-stub, nssa
    networks: List[str] = None
    virtual_links: List[str] = None
    
    def __post_init__(self):
        if self.networks is None:
            self.networks = []
        if self.virtual_links is None:
            self.virtual_links = []

class OSPFConfiguration:
    def __init__(self, process_id: int, router_id: str):
        self.process_id = process_id
        self.router_id = router_id
        self.areas: Dict[str, OSPFArea] = {}
        self.interfaces: Dict[str, Dict] = {}
        self.redistributed_routes: List[Dict] = []
        
    def add_area(self, area: OSPFArea):
        """Add OSPF area configuration"""
        self.areas[area.area_id] = area
    
    def configure_interface(self, interface_name: str, area_id: str, 
                          network_type: str = "broadcast", 
                          cost: int = None, 
                          priority: int = None):
        """Configure OSPF interface parameters"""
        self.interfaces[interface_name] = {
            'area': area_id,
            'network_type': network_type,
            'cost': cost,
            'priority': priority,
            'timers': {'hello': 10, 'dead': 40}
        }
    
    def optimize_timers(self, interface_name: str, hello_interval: int, dead_interval: int):
        """Optimize OSPF timers for faster convergence"""
        if dead_interval < 4 * hello_interval:
            raise ValueError("Dead interval should be at least 4x hello interval")
        
        if interface_name in self.interfaces:
            self.interfaces[interface_name]['timers'] = {
                'hello': hello_interval,
                'dead': dead_interval
            }
    
    def configure_stub_area(self, area_id: str, totally_stub: bool = False):
        """Configure stub area to reduce LSA flooding"""
        if area_id == "0.0.0.0":
            raise ValueError("Backbone area cannot be configured as stub")
        
        area_type = "totally-stub" if totally_stub else "stub"
        if area_id in self.areas:
            self.areas[area_id].area_type = area_type
        else:
            self.add_area(OSPFArea(area_id=area_id, area_type=area_type))
    
    def generate_cisco_config(self):
        """Generate Cisco OSPF configuration"""
        config = [
            f"router ospf {self.process_id}",
            f" router-id {self.router_id}",
            " auto-cost reference-bandwidth 100000",  # For 100G links
            " log-adjacency-changes detail"
        ]
        
        # Configure areas
        for area_id, area in self.areas.items():
            if area.area_type == "stub":
                config.append(f" area {area_id} stub")
            elif area.area_type == "totally-stub":
                config.append(f" area {area_id} stub no-summary")
            elif area.area_type == "nssa":
                config.append(f" area {area_id} nssa")
            
            # Add networks to areas
            for network in area.networks:
                config.append(f" network {network} area {area_id}")
        
        # Interface-specific configuration
        interface_config = []
        for interface_name, params in self.interfaces.items():
            interface_config.extend([
                f"interface {interface_name}",
                f" ip ospf {self.process_id} area {params['area']}"
            ])
            
            if params['cost']:
                interface_config.append(f" ip ospf cost {params['cost']}")
            
            if params['priority'] is not None:
                interface_config.append(f" ip ospf priority {params['priority']}")
            
            if params['network_type'] != "broadcast":
                interface_config.append(f" ip ospf network {params['network_type']}")
            
            # Optimize timers
            hello = params['timers']['hello']
            dead = params['timers']['dead']
            interface_config.append(f" ip ospf hello-interval {hello}")
            interface_config.append(f" ip ospf dead-interval {dead}")
        
        return "\n".join(config), "\n".join(interface_config)

# Example: Multi-area OSPF design for campus network
campus_ospf = OSPFConfiguration(process_id=1, router_id="10.255.1.1")

# Configure backbone area
backbone = OSPFArea(area_id="0.0.0.0")
backbone.networks = ["10.255.0.0/16"]  # Loopbacks and inter-area links
campus_ospf.add_area(backbone)

# Configure access areas as stub areas
access_area1 = OSPFArea(area_id="0.0.0.1", area_type="stub")
access_area1.networks = ["10.1.0.0/16"]
campus_ospf.add_area(access_area1)

# Configure interfaces
campus_ospf.configure_interface("GigabitEthernet0/0", "0.0.0.0", cost=1000)
campus_ospf.configure_interface("GigabitEthernet0/1", "0.0.0.1", cost=100)

# Optimize for fast convergence
campus_ospf.optimize_timers("GigabitEthernet0/0", hello_interval=1, dead_interval=4)

router_config, interface_config = campus_ospf.generate_cisco_config()
print("=== OSPF Router Configuration ===")
print(router_config)
print("\n=== Interface Configuration ===")
print(interface_config)
```

#### OSPF Performance Optimization

Modern OSPF implementations require careful tuning for optimal performance:

```python
class OSPFOptimizer:
    def __init__(self, ospf_config: OSPFConfiguration):
        self.ospf_config = ospf_config
    
    def calculate_spf_delay_optimizations(self, network_size: str):
        """Calculate optimal SPF delay timers based on network size"""
        if network_size == "small":  # < 50 routers
            return {"initial": 1000, "minimum": 5000, "maximum": 10000}
        elif network_size == "medium":  # 50-200 routers
            return {"initial": 2000, "minimum": 5000, "maximum": 20000}
        else:  # large networks
            return {"initial": 5000, "minimum": 10000, "maximum": 30000}
    
    def generate_performance_config(self, network_size: str):
        """Generate performance-optimized OSPF configuration"""
        spf_timers = self.calculate_spf_delay_optimizations(network_size)
        
        config = [
            f"router ospf {self.ospf_config.process_id}",
            f" timers throttle spf {spf_timers['initial']} {spf_timers['minimum']} {spf_timers['maximum']}",
            " timers lsa-group-pacing 240",  # LSA pacing
            " area 0.0.0.0 filter-list prefix FILTER_EXTERNALS in",  # Filter unnecessary externals
            " max-lsa 5000 75 warning-only"  # LSA database protection
        ]
        
        return "\n".join(config)
    
    def calculate_interface_costs(self, bandwidth_mbps: int):
        """Calculate OSPF cost based on interface bandwidth"""
        reference_bw = 100000  # 100 Gbps reference bandwidth
        cost = reference_bw // bandwidth_mbps
        return max(cost, 1)  # Minimum cost is 1
```

## Segment 3: Software-Defined Networking (SDN) Integration (40 minutes)

### SDN Architecture and OpenFlow Implementation

Software-Defined Networking separates the control plane from the data plane, enabling centralized network management and programmable network behavior. OpenFlow serves as the primary southbound protocol between SDN controllers and network switches.

#### OpenFlow Controller Development

Modern SDN deployments require sophisticated controller logic to manage network flows efficiently:

```python
import json
import asyncio
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from enum import Enum

class FlowTablePriority(Enum):
    DROP_ALL = 0
    DEFAULT_FORWARDING = 100
    LOAD_BALANCING = 200
    SECURITY_RULES = 300
    CRITICAL_FLOWS = 400

@dataclass
class OpenFlowRule:
    table_id: int = 0
    priority: int = 100
    match_fields: Dict = field(default_factory=dict)
    actions: List[Dict] = field(default_factory=list)
    cookie: int = 0
    idle_timeout: int = 0
    hard_timeout: int = 0
    
    def add_match(self, field_name: str, field_value: str, mask: str = None):
        """Add match field to the flow rule"""
        match_entry = {"field": field_name, "value": field_value}
        if mask:
            match_entry["mask"] = mask
        self.match_fields[field_name] = match_entry
    
    def add_action(self, action_type: str, **kwargs):
        """Add action to the flow rule"""
        action = {"type": action_type}
        action.update(kwargs)
        self.actions.append(action)
    
    def to_openflow_json(self):
        """Convert to OpenFlow JSON format"""
        return {
            "table_id": self.table_id,
            "priority": self.priority,
            "match": self.match_fields,
            "actions": self.actions,
            "cookie": self.cookie,
            "idle_timeout": self.idle_timeout,
            "hard_timeout": self.hard_timeout
        }

class SDNController:
    def __init__(self, controller_id: str):
        self.controller_id = controller_id
        self.switches: Dict[str, Dict] = {}
        self.flow_tables: Dict[str, List[OpenFlowRule]] = {}
        self.topology: Dict[str, Set[str]] = {}
        self.load_balancer_pools: Dict[str, List[str]] = {}
    
    def register_switch(self, switch_dpid: str, switch_info: Dict):
        """Register a new OpenFlow switch"""
        self.switches[switch_dpid] = switch_info
        self.flow_tables[switch_dpid] = []
        self.topology[switch_dpid] = set()
    
    def add_link(self, switch1: str, switch2: str):
        """Add bidirectional link between switches"""
        if switch1 in self.topology and switch2 in self.topology:
            self.topology[switch1].add(switch2)
            self.topology[switch2].add(switch1)
    
    def install_flow_rule(self, switch_dpid: str, flow_rule: OpenFlowRule):
        """Install flow rule on specific switch"""
        if switch_dpid not in self.flow_tables:
            raise ValueError(f"Switch {switch_dpid} not registered")
        
        # Remove any conflicting rules (same table, priority, and match)
        self.flow_tables[switch_dpid] = [
            rule for rule in self.flow_tables[switch_dpid]
            if not self._rules_conflict(rule, flow_rule)
        ]
        
        self.flow_tables[switch_dpid].append(flow_rule)
        return self._send_flow_mod(switch_dpid, flow_rule)
    
    def _rules_conflict(self, rule1: OpenFlowRule, rule2: OpenFlowRule):
        """Check if two rules conflict (same table, priority, and match)"""
        return (rule1.table_id == rule2.table_id and 
                rule1.priority == rule2.priority and
                rule1.match_fields == rule2.match_fields)
    
    def _send_flow_mod(self, switch_dpid: str, flow_rule: OpenFlowRule):
        """Send flow modification message to switch (simulated)"""
        message = {
            "type": "FLOW_MOD",
            "switch": switch_dpid,
            "flow": flow_rule.to_openflow_json()
        }
        # In real implementation, this would send OpenFlow message
        return f"Installed flow rule on {switch_dpid}: {json.dumps(message, indent=2)}"
    
    def configure_load_balancer(self, vip: str, backend_servers: List[str], 
                               load_balancing_method: str = "round_robin"):
        """Configure load balancing flows"""
        self.load_balancer_pools[vip] = backend_servers
        
        flows = []
        for i, server in enumerate(backend_servers):
            # Create flow rule for each backend server
            flow_rule = OpenFlowRule(
                priority=FlowTablePriority.LOAD_BALANCING.value,
                cookie=hash(f"{vip}_{server}")
            )
            
            # Match traffic destined to VIP
            flow_rule.add_match("eth_type", "0x0800")  # IPv4
            flow_rule.add_match("ipv4_dst", vip)
            
            if load_balancing_method == "round_robin":
                # Simple round-robin using flow cookie modulo
                flow_rule.add_match("tcp_src", f"0x{i:04x}", mask="0x000f")
            
            # Actions: rewrite destination and forward
            flow_rule.add_action("set_field", field="ipv4_dst", value=server)
            flow_rule.add_action("output", port="CONTROLLER")  # Let controller decide output
            
            flows.append(flow_rule)
        
        return flows
    
    def implement_micro_segmentation(self, security_policy: Dict):
        """Implement micro-segmentation using flow rules"""
        security_flows = []
        
        for rule in security_policy.get("allow_rules", []):
            flow_rule = OpenFlowRule(
                priority=FlowTablePriority.SECURITY_RULES.value
            )
            
            # Configure match criteria
            if "src_subnet" in rule:
                flow_rule.add_match("ipv4_src", rule["src_subnet"])
            if "dst_subnet" in rule:
                flow_rule.add_match("ipv4_dst", rule["dst_subnet"])
            if "protocol" in rule:
                flow_rule.add_match("ip_proto", rule["protocol"])
            if "dst_port" in rule:
                flow_rule.add_match("tcp_dst", rule["dst_port"])
            
            # Allow action
            flow_rule.add_action("output", port="NORMAL")
            security_flows.append(flow_rule)
        
        # Default deny rule (lowest priority)
        deny_rule = OpenFlowRule(priority=FlowTablePriority.DROP_ALL.value)
        deny_rule.add_action("drop")
        security_flows.append(deny_rule)
        
        return security_flows

# Example SDN controller usage
controller = SDNController("sdn-controller-01")

# Register switches
controller.register_switch("switch-001", {"dpid": "0x1", "ports": 48})
controller.register_switch("switch-002", {"dpid": "0x2", "ports": 48})

# Configure load balancing
web_servers = ["10.1.1.10", "10.1.1.11", "10.1.1.12"]
lb_flows = controller.configure_load_balancer("10.1.1.100", web_servers)

# Install flows on switches
for flow in lb_flows:
    result = controller.install_flow_rule("switch-001", flow)
    print(result)
```

#### Intent-Based Networking (IBN) Implementation

Intent-Based Networking represents the evolution of SDN, allowing administrators to specify high-level intentions that are automatically translated into network configurations:

```python
from abc import ABC, abstractmethod
from typing import Any

class NetworkIntent(ABC):
    def __init__(self, intent_id: str, description: str):
        self.intent_id = intent_id
        self.description = description
        self.status = "pending"
    
    @abstractmethod
    def translate_to_flows(self, controller: SDNController) -> List[OpenFlowRule]:
        """Translate high-level intent to low-level flow rules"""
        pass
    
    @abstractmethod
    def verify_compliance(self, current_state: Dict) -> bool:
        """Verify that current network state matches intent"""
        pass

class SecurityIsolationIntent(NetworkIntent):
    def __init__(self, intent_id: str, source_group: str, destination_group: str, 
                 allowed_services: List[str]):
        super().__init__(intent_id, f"Isolate {source_group} from {destination_group}")
        self.source_group = source_group
        self.destination_group = destination_group
        self.allowed_services = allowed_services
    
    def translate_to_flows(self, controller: SDNController) -> List[OpenFlowRule]:
        """Generate isolation flows"""
        flows = []
        
        # Create allow rules for specified services
        for service in self.allowed_services:
            flow = OpenFlowRule(priority=300)
            flow.add_match("ipv4_src", f"group:{self.source_group}")
            flow.add_match("ipv4_dst", f"group:{self.destination_group}")
            
            if service == "http":
                flow.add_match("tcp_dst", "80")
            elif service == "https":
                flow.add_match("tcp_dst", "443")
            elif service == "ssh":
                flow.add_match("tcp_dst", "22")
            
            flow.add_action("output", port="NORMAL")
            flows.append(flow)
        
        # Default deny rule
        deny_flow = OpenFlowRule(priority=200)
        deny_flow.add_match("ipv4_src", f"group:{self.source_group}")
        deny_flow.add_match("ipv4_dst", f"group:{self.destination_group}")
        deny_flow.add_action("drop")
        flows.append(deny_flow)
        
        return flows
    
    def verify_compliance(self, current_state: Dict) -> bool:
        """Verify isolation is properly implemented"""
        # Check if required flows are installed
        # This would analyze current flow tables
        return True  # Simplified for example

class IBNController(SDNController):
    def __init__(self, controller_id: str):
        super().__init__(controller_id)
        self.intents: List[NetworkIntent] = []
        self.intent_violations: List[str] = []
    
    def add_intent(self, intent: NetworkIntent):
        """Add new network intent"""
        self.intents.append(intent)
        self._deploy_intent(intent)
    
    def _deploy_intent(self, intent: NetworkIntent):
        """Deploy intent by translating to flow rules"""
        try:
            flows = intent.translate_to_flows(self)
            for switch_dpid in self.switches.keys():
                for flow in flows:
                    self.install_flow_rule(switch_dpid, flow)
            
            intent.status = "deployed"
        except Exception as e:
            intent.status = "failed"
            self.intent_violations.append(f"Intent {intent.intent_id} failed: {str(e)}")
    
    def continuous_verification(self):
        """Continuously verify intent compliance"""
        violations = []
        for intent in self.intents:
            if not intent.verify_compliance(self._get_network_state()):
                violations.append(intent.intent_id)
                self._remediate_intent(intent)
        
        return violations
    
    def _get_network_state(self) -> Dict:
        """Get current network state"""
        return {
            "flows": self.flow_tables,
            "topology": self.topology,
            "switches": self.switches
        }
    
    def _remediate_intent(self, intent: NetworkIntent):
        """Remediate intent violation"""
        # Re-deploy the intent
        self._deploy_intent(intent)

# Example IBN usage
ibn_controller = IBNController("ibn-controller-01")

# Define security isolation intent
web_to_db_isolation = SecurityIsolationIntent(
    intent_id="web-db-isolation-001",
    source_group="web-tier",
    destination_group="database-tier", 
    allowed_services=["https", "mysql"]
)

ibn_controller.add_intent(web_to_db_isolation)
```

## Segment 4: Network Virtualization Overlays (35 minutes)

### Overlay Network Technologies

Network virtualization overlays provide logical network abstraction over physical infrastructure, enabling multi-tenancy, network isolation, and simplified network management. Modern overlay technologies include VXLAN, STT (Stateless Transport Tunneling), and GENEVE.

#### VXLAN Overlay Implementation

Building on our earlier VXLAN discussion, let's explore comprehensive overlay network implementation:

```python
import hashlib
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class OverlayEndpoint:
    vtep_ip: str
    tunnel_endpoint_id: str
    supported_encapsulations: List[str]
    max_vnis: int = 16777215

class VXLANOverlayManager:
    def __init__(self, local_vtep_ip: str):
        self.local_vtep_ip = local_vtep_ip
        self.remote_vteps: Dict[str, OverlayEndpoint] = {}
        self.vni_assignments: Dict[int, Dict] = {}
        self.mac_table: Dict[str, Dict] = {}  # MAC to VTEP mapping
        self.arp_cache: Dict[str, Dict] = {}  # IP to MAC/VTEP mapping
        
    def register_remote_vtep(self, vtep_ip: str, endpoint_info: Dict):
        """Register remote VTEP for overlay communication"""
        endpoint = OverlayEndpoint(
            vtep_ip=vtep_ip,
            tunnel_endpoint_id=endpoint_info.get("tunnel_id", vtep_ip),
            supported_encapsulations=endpoint_info.get("encapsulations", ["vxlan"]),
            max_vnis=endpoint_info.get("max_vnis", 16777215)
        )
        self.remote_vteps[vtep_ip] = endpoint
    
    def create_overlay_network(self, vni: int, network_name: str, 
                             multicast_group: Optional[str] = None,
                             flood_mode: str = "multicast"):
        """Create new overlay network with specified VNI"""
        if vni in self.vni_assignments:
            raise ValueError(f"VNI {vni} already in use")
        
        self.vni_assignments[vni] = {
            "name": network_name,
            "flood_mode": flood_mode,
            "multicast_group": multicast_group,
            "member_vteps": set(),
            "created_at": "2025-01-01"  # In real implementation, use datetime
        }
        
        # Add local VTEP as member
        self.vni_assignments[vni]["member_vteps"].add(self.local_vtep_ip)
    
    def join_overlay_network(self, vni: int, vtep_ip: str):
        """Add VTEP to existing overlay network"""
        if vni not in self.vni_assignments:
            raise ValueError(f"VNI {vni} does not exist")
        
        if vtep_ip not in self.remote_vteps:
            raise ValueError(f"VTEP {vtep_ip} not registered")
        
        self.vni_assignments[vni]["member_vteps"].add(vtep_ip)
    
    def learn_mac_address(self, vni: int, mac_address: str, 
                         ip_address: str, source_vtep: str):
        """Learn MAC-to-VTEP mapping from data plane"""
        if vni not in self.vni_assignments:
            return False
        
        # Update MAC table
        self.mac_table[f"{vni}:{mac_address}"] = {
            "vtep": source_vtep,
            "learned_at": "2025-01-01",  # timestamp
            "age": 0
        }
        
        # Update ARP cache
        if ip_address:
            self.arp_cache[f"{vni}:{ip_address}"] = {
                "mac": mac_address,
                "vtep": source_vtep,
                "learned_at": "2025-01-01"
            }
        
        return True
    
    def lookup_destination_vtep(self, vni: int, dest_mac: str) -> Optional[str]:
        """Lookup destination VTEP for MAC address"""
        key = f"{vni}:{dest_mac}"
        if key in self.mac_table:
            return self.mac_table[key]["vtep"]
        return None
    
    def generate_vxlan_encapsulation(self, vni: int, inner_frame: bytes, 
                                   dest_vtep: str) -> Dict:
        """Generate VXLAN encapsulation for frame"""
        if dest_vtep not in self.remote_vteps:
            raise ValueError(f"Unknown destination VTEP: {dest_vtep}")
        
        # VXLAN header construction
        vxlan_header = {
            "flags": 0x08,  # VNI valid flag
            "vni": vni,
            "reserved": 0
        }
        
        # UDP header for VXLAN
        udp_header = {
            "src_port": self._generate_entropy_port(inner_frame),
            "dst_port": 4789,  # VXLAN standard port
            "length": len(inner_frame) + 8 + 8,  # UDP + VXLAN headers
            "checksum": 0  # Often disabled for performance
        }
        
        # Outer IP header
        ip_header = {
            "src_ip": self.local_vtep_ip,
            "dst_ip": dest_vtep,
            "protocol": 17,  # UDP
            "ttl": 64
        }
        
        return {
            "outer_ip": ip_header,
            "udp": udp_header,
            "vxlan": vxlan_header,
            "inner_frame": inner_frame
        }
    
    def _generate_entropy_port(self, frame: bytes) -> int:
        """Generate entropy-based source port for ECMP"""
        # Use frame hash for consistent ECMP behavior
        frame_hash = hashlib.md5(frame[:64]).hexdigest()  # First 64 bytes
        port_base = 32768  # Ephemeral port range start
        entropy = int(frame_hash[:4], 16) % 32768
        return port_base + entropy
    
    def optimize_overlay_performance(self) -> Dict[str, Any]:
        """Generate performance optimization recommendations"""
        optimizations = {
            "mtu_configuration": {
                "overlay_mtu": 1450,  # Account for VXLAN overhead
                "underlay_mtu": 1500,
                "jumbo_frames": 9000  # If supported
            },
            "offload_features": [
                "tx_checksum_offload",
                "rx_checksum_offload", 
                "tunnel_segmentation_offload",
                "generic_receive_offload"
            ],
            "buffer_tuning": {
                "socket_buffer_size": "16MB",
                "tcp_window_scaling": True,
                "tcp_timestamps": True
            }
        }
        
        return optimizations

# Example: Multi-site overlay network deployment
overlay_manager = VXLANOverlayManager(local_vtep_ip="192.168.1.10")

# Register remote VTEPs
remote_sites = [
    {"vtep_ip": "192.168.2.10", "site": "datacenter-east"},
    {"vtep_ip": "192.168.3.10", "site": "datacenter-west"},
    {"vtep_ip": "192.168.4.10", "site": "edge-location-1"}
]

for site in remote_sites:
    overlay_manager.register_remote_vtep(
        site["vtep_ip"],
        {"tunnel_id": site["site"], "encapsulations": ["vxlan", "geneve"]}
    )

# Create overlay networks for different applications
overlay_manager.create_overlay_network(100, "web-tier-prod")
overlay_manager.create_overlay_network(200, "app-tier-prod") 
overlay_manager.create_overlay_network(300, "db-tier-prod")

# Join remote VTEPs to overlay networks
for site in remote_sites:
    for vni in [100, 200, 300]:
        overlay_manager.join_overlay_network(vni, site["vtep_ip"])

print("Overlay network topology created successfully")
print(f"VNI Assignments: {overlay_manager.vni_assignments}")
```

#### GENEVE (Generic Network Virtualization Encapsulation)

GENEVE provides more flexible encapsulation compared to VXLAN, supporting extensible headers and metadata:

```python
class GENEVEManager:
    def __init__(self, local_endpoint: str):
        self.local_endpoint = local_endpoint
        self.option_classes: Dict[int, Dict] = {}
        self.tunnels: Dict[str, Dict] = {}
        
    def register_option_class(self, class_id: int, class_name: str, 
                            length: int, critical: bool = False):
        """Register GENEVE option class"""
        self.option_classes[class_id] = {
            "name": class_name,
            "length": length,
            "critical": critical
        }
    
    def create_geneve_tunnel(self, tunnel_id: str, remote_endpoint: str,
                           vni: int, options: List[Dict] = None):
        """Create GENEVE tunnel with options"""
        if options is None:
            options = []
            
        tunnel_config = {
            "remote_endpoint": remote_endpoint,
            "vni": vni,
            "options": options,
            "protocol": "geneve",
            "port": 6081  # GENEVE standard port
        }
        
        self.tunnels[tunnel_id] = tunnel_config
        return tunnel_config
    
    def add_security_context_option(self, tunnel_id: str, security_context: str):
        """Add security context option to GENEVE header"""
        if tunnel_id not in self.tunnels:
            raise ValueError(f"Tunnel {tunnel_id} not found")
        
        # Security context option (example class ID 0x0101)
        security_option = {
            "class": 0x0101,
            "type": 0x01,
            "length": len(security_context.encode()) // 4 + 1,
            "data": security_context.encode()
        }
        
        self.tunnels[tunnel_id]["options"].append(security_option)
    
    def generate_packet_trace_option(self, trace_id: str) -> Dict:
        """Generate packet tracing option for network troubleshooting"""
        return {
            "class": 0x0102,  # Custom tracing class
            "type": 0x01,
            "length": 4,  # 16 bytes / 4
            "data": trace_id.encode()[:16].ljust(16, b'\x00')
        }

# Example GENEVE usage
geneve_mgr = GENEVEManager("10.0.1.100")

# Register custom option classes
geneve_mgr.register_option_class(0x0101, "security_context", 4, critical=True)
geneve_mgr.register_option_class(0x0102, "packet_trace", 4, critical=False)

# Create tunnel with security context
tunnel = geneve_mgr.create_geneve_tunnel(
    "tunnel-to-remote-dc",
    "10.0.2.100",
    vni=1000
)

geneve_mgr.add_security_context_option("tunnel-to-remote-dc", "production-dmz")
```

## Segment 5: Automation and Infrastructure as Code (30 minutes)

### Network Infrastructure Automation

Modern network operations require comprehensive automation to manage complex topologies, ensure consistency, and enable rapid deployment. Infrastructure as Code (IaC) principles applied to networking provide version control, repeatability, and scalability.

#### Network Configuration Management with Ansible

Ansible provides powerful network automation capabilities for configuration management across diverse network devices:

```python
# network_automation_framework.py
import yaml
import jinja2
from typing import Dict, List, Any
from dataclasses import dataclass, field

@dataclass
class NetworkDevice:
    hostname: str
    device_type: str  # cisco_ios, juniper_junos, arista_eos
    management_ip: str
    platform: str
    credentials: Dict[str, str]
    interfaces: List[Dict] = field(default_factory=list)
    routing_config: Dict = field(default_factory=dict)
    vlans: List[Dict] = field(default_factory=list)

class NetworkAutomationFramework:
    def __init__(self, inventory_file: str):
        self.inventory = self._load_inventory(inventory_file)
        self.templates = {}
        self.playbooks = {}
        
    def _load_inventory(self, inventory_file: str) -> Dict[str, NetworkDevice]:
        """Load network device inventory from YAML"""
        with open(inventory_file, 'r') as f:
            inventory_data = yaml.safe_load(f)
        
        devices = {}
        for device_data in inventory_data.get('devices', []):
            device = NetworkDevice(
                hostname=device_data['hostname'],
                device_type=device_data['device_type'],
                management_ip=device_data['management_ip'],
                platform=device_data['platform'],
                credentials=device_data['credentials']
            )
            devices[device.hostname] = device
        
        return devices
    
    def generate_vlan_configuration(self, device: NetworkDevice, 
                                  vlan_database: List[Dict]) -> str:
        """Generate VLAN configuration for device"""
        template_str = """
{%- for vlan in vlans %}
vlan {{ vlan.id }}
 name {{ vlan.name }}
{%- if vlan.description %}
 description {{ vlan.description }}
{%- endif %}
!
{%- endfor %}

{%- for interface in interfaces %}
interface {{ interface.name }}
{%- if interface.type == 'access' %}
 switchport mode access
 switchport access vlan {{ interface.vlan }}
{%- elif interface.type == 'trunk' %}
 switchport mode trunk
 switchport trunk allowed vlan {{ interface.allowed_vlans|join(',') }}
{%- endif %}
{%- if interface.description %}
 description {{ interface.description }}
{%- endif %}
!
{%- endfor %}
        """
        
        template = jinja2.Template(template_str)
        return template.render(vlans=vlan_database, interfaces=device.interfaces)
    
    def generate_ospf_configuration(self, device: NetworkDevice,
                                   ospf_config: Dict) -> str:
        """Generate OSPF configuration"""
        template_str = """
router ospf {{ process_id }}
 router-id {{ router_id }}
{%- for area in areas %}
{%- for network in area.networks %}
 network {{ network }} area {{ area.id }}
{%- endfor %}
{%- if area.type == 'stub' %}
 area {{ area.id }} stub
{%- elif area.type == 'nssa' %}
 area {{ area.id }} nssa
{%- endif %}
{%- endfor %}
!
        """
        
        template = jinja2.Template(template_str)
        return template.render(**ospf_config)
    
    def generate_ansible_playbook(self, task_name: str, 
                                 device_group: str,
                                 configuration_template: str) -> str:
        """Generate Ansible playbook for network configuration"""
        playbook_template = """
---
- name: {{ task_name }}
  hosts: {{ device_group }}
  gather_facts: no
  connection: network_cli
  
  tasks:
    - name: Apply configuration
      {{ platform_module }}:
        lines: |
{{ configuration | indent(10) }}
        save_when: always
      register: config_result
    
    - name: Display configuration result
      debug:
        var: config_result
        """
        
        # Determine platform-specific module
        platform_modules = {
            'cisco_ios': 'ios_config',
            'juniper_junos': 'junos_config', 
            'arista_eos': 'eos_config'
        }
        
        # Get first device to determine platform
        first_device = next(iter(self.inventory.values()))
        platform_module = platform_modules.get(first_device.device_type, 'ios_config')
        
        template = jinja2.Template(playbook_template)
        return template.render(
            task_name=task_name,
            device_group=device_group,
            platform_module=platform_module,
            configuration=configuration_template
        )
    
    def validate_configuration_drift(self, device: NetworkDevice,
                                   expected_config: str) -> Dict[str, Any]:
        """Validate configuration against expected state"""
        # This would integrate with network testing frameworks
        # like pyATS or Batfish for comprehensive validation
        validation_result = {
            "device": device.hostname,
            "compliant": True,
            "drift_detected": [],
            "validation_tests": [
                {"test": "VLAN_existence", "status": "PASS"},
                {"test": "OSPF_neighbor_adjacency", "status": "PASS"},
                {"test": "Interface_status", "status": "PASS"}
            ]
        }
        
        return validation_result

# Example inventory file (inventory.yml)
inventory_yaml = """
devices:
  - hostname: spine-01
    device_type: cisco_ios
    management_ip: 10.0.0.1
    platform: catalyst_9000
    credentials:
      username: admin
      password_env_var: DEVICE_PASSWORD
  
  - hostname: leaf-01  
    device_type: cisco_ios
    management_ip: 10.0.0.10
    platform: catalyst_9000
    credentials:
      username: admin
      password_env_var: DEVICE_PASSWORD
"""

# Save inventory file
with open('/tmp/inventory.yml', 'w') as f:
    f.write(inventory_yaml)

# Initialize automation framework
automation = NetworkAutomationFramework('/tmp/inventory.yml')

# Generate VLAN configuration
vlan_db = [
    {"id": 100, "name": "WEB_TIER", "description": "Web servers"},
    {"id": 200, "name": "APP_TIER", "description": "Application servers"},
    {"id": 300, "name": "DB_TIER", "description": "Database servers"}
]

device = automation.inventory['leaf-01']
device.interfaces = [
    {"name": "GigabitEthernet1/0/1", "type": "access", "vlan": 100},
    {"name": "GigabitEthernet1/0/24", "type": "trunk", "allowed_vlans": [100, 200, 300]}
]

vlan_config = automation.generate_vlan_configuration(device, vlan_db)
print("=== Generated VLAN Configuration ===")
print(vlan_config)
```

#### Terraform for Network Infrastructure

Terraform enables infrastructure as code for network provisioning across cloud and on-premises environments:

```python
# terraform_network_generator.py
class TerraformNetworkGenerator:
    def __init__(self, provider: str = "aws"):
        self.provider = provider
        self.resources = []
        self.variables = {}
        self.outputs = {}
    
    def add_variable(self, name: str, type_: str, description: str, 
                    default_value: Any = None):
        """Add Terraform variable"""
        variable = {
            "type": type_,
            "description": description
        }
        if default_value is not None:
            variable["default"] = default_value
        
        self.variables[name] = variable
    
    def create_vpc_network(self, vpc_name: str, cidr_block: str, 
                          availability_zones: List[str]) -> str:
        """Generate VPC network configuration"""
        vpc_config = f"""
resource "aws_vpc" "{vpc_name}" {{
  cidr_block           = "{cidr_block}"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {{
    Name = "{vpc_name}"
    Environment = var.environment
  }}
}}

resource "aws_internet_gateway" "{vpc_name}_igw" {{
  vpc_id = aws_vpc.{vpc_name}.id
  
  tags = {{
    Name = "{vpc_name}-igw"
  }}
}}
        """
        
        # Generate subnets for each AZ
        subnet_configs = []
        for i, az in enumerate(availability_zones):
            for subnet_type in ['public', 'private']:
                subnet_offset = i * 4 + (0 if subnet_type == 'public' else 2)
                subnet_cidr = self._calculate_subnet_cidr(cidr_block, subnet_offset)
                
                subnet_config = f"""
resource "aws_subnet" "{vpc_name}_{subnet_type}_{i+1}" {{
  vpc_id            = aws_vpc.{vpc_name}.id
  cidr_block        = "{subnet_cidr}"
  availability_zone = "{az}"
  
  {f'map_public_ip_on_launch = true' if subnet_type == 'public' else ''}
  
  tags = {{
    Name = "{vpc_name}-{subnet_type}-{i+1}"
    Type = "{subnet_type}"
  }}
}}
                """
                subnet_configs.append(subnet_config)
        
        return vpc_config + "\n".join(subnet_configs)
    
    def _calculate_subnet_cidr(self, vpc_cidr: str, subnet_offset: int) -> str:
        """Calculate subnet CIDR based on VPC CIDR and offset"""
        import ipaddress
        vpc_network = ipaddress.ip_network(vpc_cidr)
        subnets = list(vpc_network.subnets(new_prefix=24))
        if subnet_offset < len(subnets):
            return str(subnets[subnet_offset])
        raise ValueError(f"Subnet offset {subnet_offset} exceeds available subnets")
    
    def create_security_groups(self, vpc_name: str, 
                              security_rules: List[Dict]) -> str:
        """Generate security group configurations"""
        sg_configs = []
        
        for rule_group in security_rules:
            sg_name = rule_group['name']
            sg_config = f"""
resource "aws_security_group" "{sg_name}" {{
  name_prefix = "{sg_name}-"
  vpc_id      = aws_vpc.{vpc_name}.id
  description = "{rule_group.get('description', '')}"
  
            """
            
            # Ingress rules
            for rule in rule_group.get('ingress', []):
                sg_config += f"""
  ingress {{
    from_port   = {rule['from_port']}
    to_port     = {rule['to_port']}
    protocol    = "{rule['protocol']}"
    cidr_blocks = {rule['cidr_blocks']}
  }}
                """
            
            # Egress rules
            for rule in rule_group.get('egress', []):
                sg_config += f"""
  egress {{
    from_port   = {rule['from_port']}
    to_port     = {rule['to_port']}
    protocol    = "{rule['protocol']}"
    cidr_blocks = {rule['cidr_blocks']}
  }}
                """
            
            sg_config += "\n}"
            sg_configs.append(sg_config)
        
        return "\n".join(sg_configs)
    
    def generate_complete_configuration(self) -> str:
        """Generate complete Terraform configuration"""
        config = f"""
terraform {{
  required_version = ">= 1.0"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = var.aws_region
}}
        """
        
        # Add variables
        if self.variables:
            for var_name, var_config in self.variables.items():
                config += f"""
variable "{var_name}" {{
  type        = {var_config['type']}
  description = "{var_config['description']}"
  {f'default = {var_config["default"]}' if 'default' in var_config else ''}
}}
                """
        
        # Add resources
        config += "\n".join(self.resources)
        
        # Add outputs
        if self.outputs:
            for output_name, output_config in self.outputs.items():
                config += f"""
output "{output_name}" {{
  value       = {output_config['value']}
  description = "{output_config['description']}"
}}
                """
        
        return config

# Example Terraform generation
tf_generator = TerraformNetworkGenerator("aws")

# Add variables
tf_generator.add_variable("aws_region", "string", "AWS region", "us-west-2")
tf_generator.add_variable("environment", "string", "Environment name", "production")

# Generate VPC configuration
vpc_config = tf_generator.create_vpc_network(
    "main_vpc",
    "10.0.0.0/16", 
    ["us-west-2a", "us-west-2b", "us-west-2c"]
)
tf_generator.resources.append(vpc_config)

# Generate security groups
security_rules = [
    {
        "name": "web_sg",
        "description": "Security group for web servers",
        "ingress": [
            {"from_port": 80, "to_port": 80, "protocol": "tcp", "cidr_blocks": ["0.0.0.0/0"]},
            {"from_port": 443, "to_port": 443, "protocol": "tcp", "cidr_blocks": ["0.0.0.0/0"]}
        ],
        "egress": [
            {"from_port": 0, "to_port": 0, "protocol": "-1", "cidr_blocks": ["0.0.0.0/0"]}
        ]
    }
]

sg_config = tf_generator.create_security_groups("main_vpc", security_rules)
tf_generator.resources.append(sg_config)

# Add outputs
tf_generator.outputs["vpc_id"] = {
    "value": "aws_vpc.main_vpc.id",
    "description": "ID of the VPC"
}

# Generate complete configuration
complete_config = tf_generator.generate_complete_configuration()
print("=== Generated Terraform Configuration ===")
print(complete_config)
```

## Conclusion and Key Takeaways

This deep dive into network topology implementation details has covered the practical aspects of building production-ready distributed systems networking infrastructure. Let's summarize the critical insights:

### Implementation Excellence

**VLAN and VXLAN Mastery**: Traditional VLANs provide the foundation for network segmentation, but VXLAN overlays enable true network virtualization at scale. The 24-bit VNI space of VXLAN (16M+ networks vs 4K VLANs) makes multi-tenant cloud environments possible.

**Routing Protocol Optimization**: BGP has evolved beyond internet routing to become the backbone of data center networking. EVPN with VXLAN provides the control plane sophistication needed for modern overlay networks, while OSPF remains critical for campus and enterprise networks.

**SDN and Intent-Based Networking**: Software-defined approaches enable network programmability and automation. Intent-based networking represents the next evolution, allowing high-level business requirements to be automatically translated into low-level network configurations.

### Production Considerations

**Performance Optimization**: Network virtualization introduces overhead that must be carefully managed. Hardware offload features, proper MTU sizing, and ECMP optimization are critical for maintaining performance at scale.

**Operational Excellence**: Infrastructure as code principles applied to networking ensure consistency, version control, and rapid deployment capabilities. Tools like Ansible and Terraform have become essential for managing complex network topologies.

**Monitoring and Troubleshooting**: Modern network overlays require sophisticated monitoring capabilities. Packet tracing through overlay networks, flow-based monitoring, and intent verification become critical operational requirements.

### Future Directions

The networking landscape continues evolving with trends toward:
- Greater integration of AI/ML for network optimization and anomaly detection
- Edge computing driving more distributed network architectures  
- Quantum-safe networking protocols preparing for post-quantum cryptography
- Network-as-a-Service models abstracting infrastructure complexity

Understanding these implementation details provides the foundation for building scalable, resilient distributed systems that can adapt to future technological changes while maintaining operational excellence today.

The next episode will explore network security implementation, diving deep into zero-trust architectures, micro-segmentation, and distributed security policy enforcement across these complex network topologies.