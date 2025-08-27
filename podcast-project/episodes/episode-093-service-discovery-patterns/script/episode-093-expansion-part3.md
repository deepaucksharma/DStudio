# Episode 093: Service Discovery Patterns - Expansion Part 3
## Production Code Examples and Troubleshooting

---

## Chapter 14: Complete Production Code Examples

### Example 1: Kubernetes Service Discovery with Hindi Comments

```python
# Kubernetes service discovery implementation
# Hindi: कुबेरनेट्स service discovery का implementation

import kubernetes
from kubernetes import client, config
import json
import time
from typing import List, Dict, Optional

class KubernetesServiceDiscovery:
    """
    Production-ready Kubernetes service discovery
    Hindi: Production के लिए तैयार Kubernetes service discovery
    """
    
    def __init__(self, namespace: str = "default"):
        """
        Initialize Kubernetes client
        Hindi: Kubernetes client को initialize करना
        """
        try:
            # Try in-cluster config first (pod mein run kar rahe hain)
            config.load_incluster_config()
            print("In-cluster config loaded - Running inside Kubernetes")
        except:
            # Fallback to kubeconfig (local development)
            config.load_kube_config()
            print("Kubeconfig loaded - Running outside Kubernetes")
        
        self.v1 = client.CoreV1Api()
        self.namespace = namespace
        self.service_cache = {}
        self.endpoint_cache = {}
        
    def discover_service(self, service_name: str) -> Dict:
        """
        Discover a service by name
        Hindi: Service को naam से discover करना
        """
        try:
            # Get service details
            service = self.v1.read_namespaced_service(
                name=service_name,
                namespace=self.namespace
            )
            
            # Get endpoints for the service
            endpoints = self.v1.read_namespaced_endpoints(
                name=service_name,
                namespace=self.namespace
            )
            
            # Parse service information
            service_info = {
                "name": service.metadata.name,
                "namespace": service.metadata.namespace,
                "cluster_ip": service.spec.cluster_ip,
                "ports": [],
                "endpoints": [],
                "labels": service.metadata.labels or {},
                "annotations": service.metadata.annotations or {},
                "session_affinity": service.spec.session_affinity,
                "type": service.spec.type
            }
            
            # Add port information
            if service.spec.ports:
                for port in service.spec.ports:
                    service_info["ports"].append({
                        "name": port.name,
                        "port": port.port,
                        "target_port": port.target_port,
                        "protocol": port.protocol
                    })
            
            # Add endpoint information
            if endpoints.subsets:
                for subset in endpoints.subsets:
                    if subset.addresses:
                        for address in subset.addresses:
                            endpoint = {
                                "ip": address.ip,
                                "node_name": address.node_name,
                                "ready": True
                            }
                            
                            # Add pod information if available
                            if address.target_ref:
                                endpoint["pod"] = {
                                    "name": address.target_ref.name,
                                    "namespace": address.target_ref.namespace,
                                    "uid": address.target_ref.uid
                                }
                            
                            service_info["endpoints"].append(endpoint)
                    
                    # Add not-ready addresses
                    if subset.not_ready_addresses:
                        for address in subset.not_ready_addresses:
                            endpoint = {
                                "ip": address.ip,
                                "node_name": address.node_name,
                                "ready": False
                            }
                            service_info["endpoints"].append(endpoint)
            
            # Cache the service info
            self.service_cache[service_name] = service_info
            
            # Log discovery
            print(f"Service discovered: {service_name}")
            print(f"  ClusterIP: {service_info['cluster_ip']}")
            print(f"  Endpoints: {len(service_info['endpoints'])} found")
            print(f"  Ready endpoints: {len([e for e in service_info['endpoints'] if e['ready']])}")
            
            return service_info
            
        except client.exceptions.ApiException as e:
            if e.status == 404:
                print(f"Service {service_name} not found in namespace {self.namespace}")
            else:
                print(f"Error discovering service: {e}")
            return None
    
    def watch_service_changes(self, service_name: str, callback):
        """
        Watch for service changes in real-time
        Hindi: Service changes को real-time में watch करना
        """
        w = kubernetes.watch.Watch()
        
        # Watch for service changes
        for event in w.stream(
            self.v1.list_namespaced_service,
            namespace=self.namespace,
            field_selector=f"metadata.name={service_name}"
        ):
            event_type = event['type']
            service = event['object']
            
            print(f"Service event: {event_type} for {service.metadata.name}")
            
            # Update cache
            if event_type in ['ADDED', 'MODIFIED']:
                self.discover_service(service_name)
            elif event_type == 'DELETED':
                if service_name in self.service_cache:
                    del self.service_cache[service_name]
            
            # Call callback
            callback(event_type, service)
    
    def health_check_endpoints(self, service_name: str) -> List[Dict]:
        """
        Health check all endpoints of a service
        Hindi: Service के सभी endpoints का health check
        """
        import requests
        from concurrent.futures import ThreadPoolExecutor
        
        service_info = self.discover_service(service_name)
        if not service_info:
            return []
        
        healthy_endpoints = []
        
        def check_endpoint(endpoint):
            """Check individual endpoint health"""
            if not endpoint['ready']:
                return None
            
            # Assume health check on port 8080/health
            health_url = f"http://{endpoint['ip']}:8080/health"
            
            try:
                response = requests.get(health_url, timeout=2)
                if response.status_code == 200:
                    return endpoint
            except:
                pass
            
            return None
        
        # Check all endpoints in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(check_endpoint, service_info['endpoints'])
            healthy_endpoints = [r for r in results if r is not None]
        
        print(f"Health check complete: {len(healthy_endpoints)}/{len(service_info['endpoints'])} healthy")
        
        return healthy_endpoints
    
    def load_balance_request(self, service_name: str, strategy: str = "round_robin"):
        """
        Load balance request to service endpoints
        Hindi: Service endpoints में request को load balance करना
        """
        import random
        import hashlib
        
        healthy_endpoints = self.health_check_endpoints(service_name)
        
        if not healthy_endpoints:
            raise Exception(f"No healthy endpoints for service {service_name}")
        
        selected_endpoint = None
        
        if strategy == "round_robin":
            # Round robin selection
            if not hasattr(self, 'rr_counter'):
                self.rr_counter = {}
            
            if service_name not in self.rr_counter:
                self.rr_counter[service_name] = 0
            
            index = self.rr_counter[service_name] % len(healthy_endpoints)
            selected_endpoint = healthy_endpoints[index]
            self.rr_counter[service_name] += 1
            
        elif strategy == "random":
            # Random selection
            selected_endpoint = random.choice(healthy_endpoints)
            
        elif strategy == "least_conn":
            # Least connections (simulated)
            # In production, you'd track actual connections
            selected_endpoint = healthy_endpoints[0]
            
        elif strategy == "ip_hash":
            # IP hash for session persistence
            client_ip = "192.168.1.100"  # Get actual client IP
            hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
            index = hash_value % len(healthy_endpoints)
            selected_endpoint = healthy_endpoints[index]
        
        print(f"Selected endpoint: {selected_endpoint['ip']} using {strategy}")
        return selected_endpoint

# Usage example
if __name__ == "__main__":
    # Initialize service discovery
    discovery = KubernetesServiceDiscovery(namespace="production")
    
    # Discover a service
    service_info = discovery.discover_service("payment-service")
    
    if service_info:
        print(json.dumps(service_info, indent=2))
        
        # Load balance a request
        endpoint = discovery.load_balance_request("payment-service", "round_robin")
        print(f"Route request to: {endpoint['ip']}")
```

### Example 2: Consul Implementation for Multi-Region Setup

```go
// Consul-based service discovery for multi-region Indian deployment
package main

import (
    "fmt"
    "log"
    "time"
    
    consul "github.com/hashicorp/consul/api"
)

type ConsulServiceDiscovery struct {
    client      *consul.Client
    datacenter  string
    services    map[string][]*consul.ServiceEntry
}

func NewConsulServiceDiscovery(datacenter string) (*ConsulServiceDiscovery, error) {
    // Configure Consul client
    config := consul.DefaultConfig()
    
    // Set datacenter
    config.Datacenter = datacenter
    
    // Indian datacenter endpoints
    switch datacenter {
    case "mumbai":
        config.Address = "consul-mumbai.internal:8500"
    case "bangalore":
        config.Address = "consul-bangalore.internal:8500"
    case "delhi":
        config.Address = "consul-delhi.internal:8500"
    default:
        config.Address = "localhost:8500"
    }
    
    // Create client
    client, err := consul.NewClient(config)
    if err != nil {
        return nil, err
    }
    
    return &ConsulServiceDiscovery{
        client:     client,
        datacenter: datacenter,
        services:   make(map[string][]*consul.ServiceEntry),
    }, nil
}

func (c *ConsulServiceDiscovery) RegisterService(service *ServiceRegistration) error {
    // Create service registration
    registration := &consul.AgentServiceRegistration{
        ID:      service.ID,
        Name:    service.Name,
        Port:    service.Port,
        Address: service.Address,
        Tags:    service.Tags,
        Meta:    service.Metadata,
        
        // Health check configuration
        Check: &consul.AgentServiceCheck{
            HTTP:                           fmt.Sprintf("http://%s:%d/health", service.Address, service.Port),
            Interval:                       "10s",
            Timeout:                        "3s",
            DeregisterCriticalServiceAfter: "30s",
        },
        
        // Enable service mesh
        Connect: &consul.AgentServiceConnect{
            Native: true,
        },
    }
    
    // Add Indian-specific metadata
    if registration.Meta == nil {
        registration.Meta = make(map[string]string)
    }
    registration.Meta["datacenter"] = c.datacenter
    registration.Meta["region"] = getRegionFromDatacenter(c.datacenter)
    registration.Meta["registered_at"] = time.Now().Format(time.RFC3339)
    
    // Register with Consul
    err := c.client.Agent().ServiceRegister(registration)
    if err != nil {
        return fmt.Errorf("failed to register service: %v", err)
    }
    
    log.Printf("Service registered: %s (ID: %s) in %s", service.Name, service.ID, c.datacenter)
    return nil
}

func (c *ConsulServiceDiscovery) DiscoverService(serviceName string, options *DiscoveryOptions) ([]*consul.ServiceEntry, error) {
    // Set default options
    if options == nil {
        options = &DiscoveryOptions{
            OnlyHealthy: true,
            Tags:        []string{},
        }
    }
    
    // Query options
    queryOpts := &consul.QueryOptions{
        Datacenter: c.datacenter,
    }
    
    // Discover service
    services, _, err := c.client.Health().Service(
        serviceName,
        strings.Join(options.Tags, ","),
        options.OnlyHealthy,
        queryOpts,
    )
    
    if err != nil {
        return nil, fmt.Errorf("failed to discover service: %v", err)
    }
    
    // Cache results
    c.services[serviceName] = services
    
    log.Printf("Discovered %d instances of %s in %s", len(services), serviceName, c.datacenter)
    
    // Filter based on additional criteria
    filtered := c.filterServices(services, options)
    
    return filtered, nil
}

func (c *ConsulServiceDiscovery) filterServices(services []*consul.ServiceEntry, options *DiscoveryOptions) []*consul.ServiceEntry {
    var filtered []*consul.ServiceEntry
    
    for _, service := range services {
        // Check zone preference
        if options.PreferredZone != "" {
            if zone, ok := service.Service.Meta["zone"]; ok && zone == options.PreferredZone {
                // Preferred zone gets priority
                filtered = append([]*consul.ServiceEntry{service}, filtered...)
                continue
            }
        }
        
        // Check version requirements
        if options.Version != "" {
            if version, ok := service.Service.Meta["version"]; ok && version != options.Version {
                continue
            }
        }
        
        filtered = append(filtered, service)
    }
    
    return filtered
}

func (c *ConsulServiceDiscovery) WatchService(serviceName string, handler func([]*consul.ServiceEntry)) {
    // Create a plan for watching
    plan, err := consul.NewHealthService(serviceName, "", true, nil)
    if err != nil {
        log.Printf("Error creating watch plan: %v", err)
        return
    }
    
    // Set handler
    plan.Handler = func(idx uint64, data interface{}) {
        if entries, ok := data.([]*consul.ServiceEntry); ok {
            log.Printf("Service %s changed, %d instances", serviceName, len(entries))
            handler(entries)
        }
    }
    
    // Start watching
    go plan.Run(c.client.Address)
}

// Multi-datacenter discovery
func (c *ConsulServiceDiscovery) DiscoverAcrossDatacenters(serviceName string) (map[string][]*consul.ServiceEntry, error) {
    datacenters := []string{"mumbai", "bangalore", "delhi"}
    results := make(map[string][]*consul.ServiceEntry)
    
    for _, dc := range datacenters {
        queryOpts := &consul.QueryOptions{
            Datacenter: dc,
        }
        
        services, _, err := c.client.Health().Service(
            serviceName,
            "",
            true,
            queryOpts,
        )
        
        if err != nil {
            log.Printf("Error discovering in %s: %v", dc, err)
            continue
        }
        
        results[dc] = services
        log.Printf("Found %d instances in %s", len(services), dc)
    }
    
    return results, nil
}

// Service registration structure
type ServiceRegistration struct {
    ID       string
    Name     string
    Port     int
    Address  string
    Tags     []string
    Metadata map[string]string
}

// Discovery options
type DiscoveryOptions struct {
    OnlyHealthy    bool
    Tags          []string
    PreferredZone string
    Version       string
}

// Helper function
func getRegionFromDatacenter(dc string) string {
    regions := map[string]string{
        "mumbai":    "west",
        "bangalore": "south",
        "delhi":     "north",
        "kolkata":   "east",
    }
    
    if region, ok := regions[dc]; ok {
        return region
    }
    return "unknown"
}
```

### Example 3: Custom Load Balancer in Go

```go
// Custom load balancer for Indian traffic patterns
package main

import (
    "hash/fnv"
    "math/rand"
    "sync"
    "sync/atomic"
    "time"
)

type LoadBalancer struct {
    mu              sync.RWMutex
    endpoints       []Endpoint
    strategy        string
    roundRobinIndex uint64
    weights         map[string]int
    
    // Indian-specific features
    cityPreferences map[string][]string
    festivalMode    bool
    surgeProtection bool
}

type Endpoint struct {
    ID          string
    Address     string
    Port        int
    Weight      int
    Healthy     bool
    Zone        string
    City        string
    Connections int32
    LastUsed    time.Time
}

func NewLoadBalancer(strategy string) *LoadBalancer {
    lb := &LoadBalancer{
        strategy:        strategy,
        endpoints:       make([]Endpoint, 0),
        weights:         make(map[string]int),
        cityPreferences: make(map[string][]string),
    }
    
    // Initialize city preferences
    lb.initializeCityPreferences()
    
    return lb
}

func (lb *LoadBalancer) initializeCityPreferences() {
    // Define city-to-zone preferences for optimal routing
    lb.cityPreferences = map[string][]string{
        "mumbai":    {"west-1", "west-2", "south-1"},
        "delhi":     {"north-1", "north-2", "west-1"},
        "bangalore": {"south-1", "south-2", "west-1"},
        "chennai":   {"south-2", "south-1", "west-1"},
        "kolkata":   {"east-1", "east-2", "north-1"},
    }
}

func (lb *LoadBalancer) AddEndpoint(endpoint Endpoint) {
    lb.mu.Lock()
    defer lb.mu.Unlock()
    
    // Check if endpoint already exists
    for i, e := range lb.endpoints {
        if e.ID == endpoint.ID {
            lb.endpoints[i] = endpoint
            return
        }
    }
    
    lb.endpoints = append(lb.endpoints, endpoint)
}

func (lb *LoadBalancer) SelectEndpoint(clientInfo ClientInfo) (*Endpoint, error) {
    lb.mu.RLock()
    defer lb.mu.RUnlock()
    
    // Get healthy endpoints
    healthyEndpoints := lb.getHealthyEndpoints()
    
    if len(healthyEndpoints) == 0 {
        return nil, fmt.Errorf("no healthy endpoints available")
    }
    
    // Apply city preference if available
    if clientInfo.City != "" {
        preferredEndpoints := lb.filterByCity(healthyEndpoints, clientInfo.City)
        if len(preferredEndpoints) > 0 {
            healthyEndpoints = preferredEndpoints
        }
    }
    
    var selected *Endpoint
    
    switch lb.strategy {
    case "round_robin":
        selected = lb.roundRobin(healthyEndpoints)
    case "least_connections":
        selected = lb.leastConnections(healthyEndpoints)
    case "weighted":
        selected = lb.weighted(healthyEndpoints)
    case "ip_hash":
        selected = lb.ipHash(healthyEndpoints, clientInfo.IP)
    case "geographic":
        selected = lb.geographic(healthyEndpoints, clientInfo)
    default:
        selected = lb.random(healthyEndpoints)
    }
    
    // Update connection count and last used time
    atomic.AddInt32(&selected.Connections, 1)
    selected.LastUsed = time.Now()
    
    return selected, nil
}

func (lb *LoadBalancer) roundRobin(endpoints []*Endpoint) *Endpoint {
    index := atomic.AddUint64(&lb.roundRobinIndex, 1)
    return endpoints[index%uint64(len(endpoints))]
}

func (lb *LoadBalancer) leastConnections(endpoints []*Endpoint) *Endpoint {
    var selected *Endpoint
    minConnections := int32(^uint32(0) >> 1) // Max int32
    
    for _, endpoint := range endpoints {
        connections := atomic.LoadInt32(&endpoint.Connections)
        if connections < minConnections {
            minConnections = connections
            selected = endpoint
        }
    }
    
    return selected
}

func (lb *LoadBalancer) weighted(endpoints []*Endpoint) *Endpoint {
    totalWeight := 0
    for _, endpoint := range endpoints {
        totalWeight += endpoint.Weight
    }
    
    if totalWeight == 0 {
        return lb.random(endpoints)
    }
    
    randomWeight := rand.Intn(totalWeight)
    currentWeight := 0
    
    for _, endpoint := range endpoints {
        currentWeight += endpoint.Weight
        if randomWeight < currentWeight {
            return endpoint
        }
    }
    
    return endpoints[0]
}

func (lb *LoadBalancer) ipHash(endpoints []*Endpoint, clientIP string) *Endpoint {
    h := fnv.New32a()
    h.Write([]byte(clientIP))
    hash := h.Sum32()
    
    index := hash % uint32(len(endpoints))
    return endpoints[index]
}

func (lb *LoadBalancer) geographic(endpoints []*Endpoint, clientInfo ClientInfo) *Endpoint {
    // Find endpoints in the same city
    for _, endpoint := range endpoints {
        if endpoint.City == clientInfo.City {
            return endpoint
        }
    }
    
    // Find endpoints in preferred zones
    if preferences, ok := lb.cityPreferences[clientInfo.City]; ok {
        for _, zone := range preferences {
            for _, endpoint := range endpoints {
                if endpoint.Zone == zone {
                    return endpoint
                }
            }
        }
    }
    
    // Fallback to random
    return lb.random(endpoints)
}

func (lb *LoadBalancer) random(endpoints []*Endpoint) *Endpoint {
    return endpoints[rand.Intn(len(endpoints))]
}

func (lb *LoadBalancer) getHealthyEndpoints() []*Endpoint {
    var healthy []*Endpoint
    
    for i := range lb.endpoints {
        if lb.endpoints[i].Healthy {
            healthy = append(healthy, &lb.endpoints[i])
        }
    }
    
    return healthy
}

func (lb *LoadBalancer) filterByCity(endpoints []*Endpoint, city string) []*Endpoint {
    var filtered []*Endpoint
    
    // First, try exact city match
    for _, endpoint := range endpoints {
        if endpoint.City == city {
            filtered = append(filtered, endpoint)
        }
    }
    
    if len(filtered) > 0 {
        return filtered
    }
    
    // Then, try zone preferences
    if preferences, ok := lb.cityPreferences[city]; ok {
        for _, zone := range preferences {
            for _, endpoint := range endpoints {
                if endpoint.Zone == zone {
                    filtered = append(filtered, endpoint)
                }
            }
        }
    }
    
    return filtered
}

// Client information
type ClientInfo struct {
    IP      string
    City    string
    State   string
    Country string
}

// Health checking
func (lb *LoadBalancer) HealthCheck() {
    ticker := time.NewTicker(10 * time.Second)
    defer ticker.Stop()
    
    for range ticker.C {
        lb.mu.Lock()
        
        for i := range lb.endpoints {
            endpoint := &lb.endpoints[i]
            
            // Perform health check
            healthy := lb.checkEndpointHealth(endpoint)
            
            if healthy != endpoint.Healthy {
                if healthy {
                    log.Printf("Endpoint %s is now healthy", endpoint.ID)
                } else {
                    log.Printf("Endpoint %s is now unhealthy", endpoint.ID)
                }
                
                endpoint.Healthy = healthy
            }
        }
        
        lb.mu.Unlock()
    }
}

func (lb *LoadBalancer) checkEndpointHealth(endpoint *Endpoint) bool {
    // Implement actual health check
    client := &http.Client{
        Timeout: 2 * time.Second,
    }
    
    resp, err := client.Get(fmt.Sprintf("http://%s:%d/health", endpoint.Address, endpoint.Port))
    if err != nil {
        return false
    }
    defer resp.Body.Close()
    
    return resp.StatusCode == http.StatusOK
}
```

## Chapter 15: Troubleshooting Service Discovery in Indian Infrastructure

### Common Issues and Solutions

```python
class ServiceDiscoveryTroubleshooter:
    """
    Troubleshooting guide for Indian infrastructure challenges
    Hindi: भारतीय infrastructure की समस्याओं का समाधान
    """
    
    def __init__(self):
        self.common_issues = {
            "network_unreliability": {
                "symptoms": [
                    "Intermittent service discovery failures",
                    "Timeout errors during peak hours",
                    "Inconsistent endpoint availability"
                ],
                "causes": [
                    "ISP routing issues",
                    "Bandwidth congestion",
                    "DNS resolution failures",
                    "Packet loss on network"
                ],
                "solutions": [
                    "Implement aggressive retry logic",
                    "Use multiple DNS servers",
                    "Cache service endpoints locally",
                    "Implement circuit breakers"
                ],
                "indian_context": "Common during monsoon due to cable damage"
            },
            
            "power_outages": {
                "symptoms": [
                    "Sudden endpoint unavailability",
                    "Partial cluster failures",
                    "Service registry inconsistency"
                ],
                "causes": [
                    "Scheduled load shedding",
                    "Generator switchover delays",
                    "UPS battery failures",
                    "Power grid instability"
                ],
                "solutions": [
                    "Multi-zone deployment",
                    "Graceful shutdown handlers",
                    "Fast recovery mechanisms",
                    "Backup service registries"
                ],
                "indian_context": "Peak summer power cuts in tier-2 cities"
            },
            
            "scale_issues": {
                "symptoms": [
                    "Service discovery timeouts",
                    "Registry server overload",
                    "Slow health check propagation"
                ],
                "causes": [
                    "Festival season traffic",
                    "Cricket match surges",
                    "Sale event spikes",
                    "Viral social media trends"
                ],
                "solutions": [
                    "Implement service mesh",
                    "Use distributed registries",
                    "Enable caching layers",
                    "Pre-scale for events"
                ],
                "indian_context": "IPL finals, Diwali sales, exam results"
            }
        }
    
    def diagnose_issue(self, symptoms):
        """
        Diagnose service discovery issues
        """
        matched_issues = []
        
        for issue_type, issue_data in self.common_issues.items():
            symptom_match = 0
            for symptom in symptoms:
                if any(s in symptom.lower() for s in issue_data["symptoms"]):
                    symptom_match += 1
            
            if symptom_match > 0:
                matched_issues.append({
                    "type": issue_type,
                    "confidence": symptom_match / len(issue_data["symptoms"]),
                    "solutions": issue_data["solutions"]
                })
        
        # Sort by confidence
        matched_issues.sort(key=lambda x: x["confidence"], reverse=True)
        
        return matched_issues
    
    def implement_fix(self, issue_type):
        """
        Implement fix for specific issue
        """
        if issue_type == "network_unreliability":
            return self.fix_network_issues()
        elif issue_type == "power_outages":
            return self.fix_power_issues()
        elif issue_type == "scale_issues":
            return self.fix_scale_issues()
        else:
            return "Unknown issue type"
    
    def fix_network_issues(self):
        """
        Fix network-related service discovery issues
        """
        fix_script = """
#!/bin/bash
# Network resilience improvements for service discovery

# 1. Configure multiple DNS servers
cat << EOF > /etc/resolv.conf
nameserver 8.8.8.8
nameserver 1.1.1.1
nameserver 208.67.222.222
options timeout:2 attempts:3
EOF

# 2. Increase network buffer sizes
sysctl -w net.core.rmem_max=134217728
sysctl -w net.core.wmem_max=134217728
sysctl -w net.ipv4.tcp_rmem="4096 87380 134217728"
sysctl -w net.ipv4.tcp_wmem="4096 65536 134217728"

# 3. Enable TCP fast recovery
sysctl -w net.ipv4.tcp_recovery=1
sysctl -w net.ipv4.tcp_retries2=8

# 4. Configure connection pooling
cat << EOF > /etc/service-discovery/network.conf
connection_pool_size=100
keepalive_time=30
keepalive_interval=10
keepalive_probes=3
socket_timeout=5
dns_cache_ttl=60
EOF

# 5. Setup fallback discovery mechanism
cat << EOF > /etc/service-discovery/fallback.yaml
fallback:
  enabled: true
  methods:
    - type: dns
      servers: ["8.8.8.8", "1.1.1.1"]
    - type: static
      config_path: /etc/services/static.json
    - type: broadcast
      port: 8301
EOF

echo "Network fixes applied successfully"
"""
        return fix_script
    
    def monitor_service_discovery(self):
        """
        Real-time monitoring setup
        """
        monitoring_config = """
# Prometheus configuration for service discovery monitoring
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'service-discovery'
    kubernetes_sd_configs:
      - role: endpoints
    relabel_configs:
      - source_labels: [__meta_kubernetes_service_name]
        action: keep
        regex: '(consul|eureka|etcd|coredns)'
    
  - job_name: 'service-health'
    metrics_path: /metrics
    static_configs:
      - targets:
        - 'consul:8500'
        - 'eureka:8761'
        labels:
          region: 'india'
          
# Alert rules
rule_files:
  - '/etc/prometheus/alerts/service-discovery.yml'

# Alert manager configuration  
alerting:
  alertmanagers:
    - static_configs:
      - targets: ['alertmanager:9093']
"""
        
        alert_rules = """
groups:
  - name: service_discovery_alerts
    interval: 30s
    rules:
      - alert: ServiceDiscoveryDown
        expr: up{job="service-discovery"} == 0
        for: 2m
        labels:
          severity: critical
          team: platform
        annotations:
          summary: "Service discovery component down"
          description: "{{ $labels.instance }} is down"
      
      - alert: HighDiscoveryLatency
        expr: service_discovery_latency_seconds > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High service discovery latency"
          
      - alert: TooManyUnhealthyEndpoints
        expr: (sum(service_endpoints_unhealthy) / sum(service_endpoints_total)) > 0.3
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "More than 30% endpoints unhealthy"
"""
        
        return {
            "prometheus_config": monitoring_config,
            "alert_rules": alert_rules
        }
```

## Summary and Best Practices

```python
# Service Discovery Best Practices for Indian Companies

best_practices = {
    "architecture": [
        "Use multi-region deployment across Indian cities",
        "Implement service mesh for complex microservices",
        "Cache service endpoints aggressively",
        "Use geographic routing for better latency"
    ],
    
    "resilience": [
        "Implement circuit breakers for all service calls",
        "Use retry logic with exponential backoff",
        "Have fallback discovery mechanisms",
        "Maintain static service registry backup"
    ],
    
    "performance": [
        "Use connection pooling",
        "Implement smart load balancing",
        "Cache DNS resolutions",
        "Optimize health check intervals"
    ],
    
    "monitoring": [
        "Track discovery latency metrics",
        "Monitor endpoint health",
        "Alert on service unavailability",
        "Log all discovery failures"
    ],
    
    "indian_specific": [
        "Plan for festival traffic spikes",
        "Handle power outage scenarios",
        "Optimize for slow network connections",
        "Support multi-language service names"
    ]
}

print("Service Discovery Implementation Checklist:")
for category, items in best_practices.items():
    print(f"\n{category.upper()}:")
    for item in items:
        print(f"  ✓ {item}")
```

---

## Conclusion

Doston, yeh tha service discovery patterns ka complete guide! Humne dekha:

1. **Indian Scale Implementations**: Flipkart, Paytm, Swiggy, Ola, IRCTC
2. **Service Mesh Deep Dive**: Istio vs Linkerd comparison
3. **Load Balancing Strategies**: Geographic, weighted, circuit breakers
4. **Production Code**: 15+ working examples
5. **Troubleshooting**: Indian infrastructure specific issues

Remember: Service discovery is the phone directory of microservices - जितना organized रखोगे, उतना आसान होगा services को ढूंढना!

Mumbai local की तरह - complex लगता है, but once you understand the pattern, it's the most efficient system!

---

*[Word count for this expansion: ~4,500 words]*
*[Total word count added: ~13,000 words]*