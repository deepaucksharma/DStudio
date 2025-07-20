# Service Discovery Pattern

<div class="navigation-header">
<div class="breadcrumb">
[Home](/) → [Part III: Patterns](/patterns/) → **Service Discovery**
</div>

<div class="pattern-nav">
**Related**: [Load Balancing](/patterns/load-balancing/) • [Health Check](/patterns/health-check/) • [All Patterns](/patterns/)
</div>
</div>

**Finding services in a dynamic distributed system**

> *"In a world where services come and go, discovery is not a luxury—it's a necessity."*

<div class="pattern-context">
<h3>🧭 Pattern Context</h3>

**🔬 Primary Axioms Addressed**:
- [Axiom 3: Failure](/part1-axioms/axiom3-failure/) - Services fail and recover
- [Axiom 5: Coordination](/part1-axioms/axiom5-coordination/) - Distributed registry

**🔧 Solves These Problems**:
- Hard-coded service endpoints
- Manual configuration updates
- Service mobility
- Dynamic scaling

**🤝 Works Best With**:
- [Load Balancing](/patterns/load-balancing/) - Route to discovered services
- [Health Check](/patterns/health-check/) - Register only healthy services
- [Circuit Breaker](/patterns/circuit-breaker/) - Handle discovery failures
</div>

---

## 🎯 Level 1: Intuition

### The Phone Directory Analogy

Service discovery is like a phone directory:
- **White Pages**: Look up service by name → get address
- **Yellow Pages**: Look up by capability → get list of providers
- **411 Service**: Ask operator → get connection
- **Updates**: Numbers change, directory must be current

### Basic Service Discovery

```python
import time
from typing import Dict, List, Optional

class SimpleServiceRegistry:
    def __init__(self):
        self.services = {}  # service_name -> list of instances
        
    def register(self, service_name: str, instance_id: str, 
                 address: str, port: int, metadata: dict = None):
        """Register a service instance"""
        if service_name not in self.services:
            self.services[service_name] = []
        
        instance = {
            'id': instance_id,
            'address': address,
            'port': port,
            'metadata': metadata or {},
            'registered_at': time.time(),
            'last_heartbeat': time.time()
        }
        
        self.services[service_name].append(instance)
        return True
    
    def deregister(self, service_name: str, instance_id: str):
        """Remove a service instance"""
        if service_name in self.services:
            self.services[service_name] = [
                inst for inst in self.services[service_name]
                if inst['id'] != instance_id
            ]
    
    def discover(self, service_name: str) -> List[dict]:
        """Find all instances of a service"""
        return self.services.get(service_name, [])
    
    def discover_one(self, service_name: str) -> Optional[dict]:
        """Find single instance (round-robin)"""
        instances = self.discover(service_name)
        if instances:
            # Simple round-robin
            instance = instances[0]
            # Move to end for next time
            self.services[service_name].append(
                self.services[service_name].pop(0)
            )
            return instance
        return None
```

---

## 🏗️ Level 2: Foundation

### Service Discovery Patterns

| Pattern | Description | Use Case | Trade-offs |
|---------|-------------|----------|------------|
| **Client-Side** | Clients query registry | Microservices | Complex clients, simple infra |
| **Server-Side** | Load balancer queries | Traditional apps | Simple clients, complex infra |
| **DNS-Based** | DNS as registry | Cross-platform | Limited metadata, caching issues |
| **Gossip-Based** | P2P discovery | Large scale | Eventually consistent |

### Implementing Client-Side Discovery

```python
import random
import requests
from typing import List, Optional
from urllib.parse import urljoin

class ServiceDiscoveryClient:
    def __init__(self, registry_url: str):
        self.registry_url = registry_url
        self.cache = {}  # Local cache
        self.cache_ttl = 30  # seconds
        
    def get_service_instances(self, service_name: str) -> List[dict]:
        """Get all instances with caching"""
        # Check cache
        if service_name in self.cache:
            entry = self.cache[service_name]
            if time.time() - entry['cached_at'] < self.cache_ttl:
                return entry['instances']
        
        # Fetch from registry
        try:
            response = requests.get(
                urljoin(self.registry_url, f'/services/{service_name}')
            )
            instances = response.json()['instances']
            
            # Update cache
            self.cache[service_name] = {
                'instances': instances,
                'cached_at': time.time()
            }
            
            return instances
        except Exception as e:
            # Return cached data if available
            if service_name in self.cache:
                return self.cache[service_name]['instances']
            raise e
    
    def call_service(self, service_name: str, 
                     endpoint: str, **kwargs) -> requests.Response:
        """Call service with automatic discovery"""
        instances = self.get_service_instances(service_name)
        
        if not instances:
            raise Exception(f"No instances found for {service_name}")
        
        # Try instances until success
        errors = []
        for attempt in range(min(3, len(instances))):
            instance = self.select_instance(instances)
            
            try:
                url = f"http://{instance['address']}:{instance['port']}{endpoint}"
                response = requests.request(
                    method=kwargs.get('method', 'GET'),
                    url=url,
                    **kwargs
                )
                response.raise_for_status()
                return response
            except Exception as e:
                errors.append((instance, str(e)))
                # Remove failed instance from list
                instances = [i for i in instances if i != instance]
        
        raise Exception(f"All instances failed: {errors}")
    
    def select_instance(self, instances: List[dict]) -> dict:
        """Select instance using load balancing strategy"""
        # Could implement various strategies:
        # - Random
        # - Round-robin
        # - Least connections
        # - Response time based
        return random.choice(instances)
```

### Health-Aware Service Discovery

```python
class HealthAwareRegistry:
    def __init__(self, health_check_interval: int = 30):
        self.services = {}
        self.health_check_interval = health_check_interval
        self.health_status = {}
        
    def register_with_health_check(self, service_name: str, 
                                  instance: dict, 
                                  health_endpoint: str):
        """Register service with health check URL"""
        instance['health_endpoint'] = health_endpoint
        instance['health_status'] = 'unknown'
        instance['last_health_check'] = 0
        
        if service_name not in self.services:
            self.services[service_name] = []
        
        self.services[service_name].append(instance)
        
        # Immediate health check
        self.check_instance_health(service_name, instance)
    
    def check_instance_health(self, service_name: str, instance: dict):
        """Check health of a specific instance"""
        health_url = f"http://{instance['address']}:{instance['port']}{instance['health_endpoint']}"
        
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                instance['health_status'] = 'healthy'
                instance['last_health_check'] = time.time()
            else:
                instance['health_status'] = 'unhealthy'
        except:
            instance['health_status'] = 'unhealthy'
    
    def get_healthy_instances(self, service_name: str) -> List[dict]:
        """Return only healthy instances"""
        if service_name not in self.services:
            return []
        
        healthy = []
        for instance in self.services[service_name]:
            # Check if health check is stale
            if time.time() - instance['last_health_check'] > self.health_check_interval:
                self.check_instance_health(service_name, instance)
            
            if instance['health_status'] == 'healthy':
                healthy.append(instance)
        
        return healthy
```

---

## 🔧 Level 3: Deep Dive

### Advanced Discovery Patterns

#### Service Mesh Discovery
```python
class ServiceMeshDiscovery:
    """
    Service discovery in a service mesh (e.g., Istio)
    """
    
    def __init__(self):
        self.services = {}
        self.virtual_services = {}
        self.destination_rules = {}
        
    def register_service(self, service: dict):
        """Register service with mesh"""
        self.services[service['name']] = {
            'instances': [],
            'ports': service['ports'],
            'labels': service['labels'],
            'endpoints': []
        }
    
    def create_virtual_service(self, name: str, config: dict):
        """Define routing rules"""
        self.virtual_services[name] = {
            'hosts': config['hosts'],
            'http_routes': config.get('http', []),
            'tcp_routes': config.get('tcp', []),
            'match_conditions': config.get('match', [])
        }
    
    def create_destination_rule(self, name: str, config: dict):
        """Define load balancing and circuit breaker config"""
        self.destination_rules[name] = {
            'host': config['host'],
            'traffic_policy': config.get('trafficPolicy', {}),
            'subsets': config.get('subsets', []),
            'connection_pool': config.get('connectionPool', {})
        }
    
    def route_request(self, request: dict) -> Optional[dict]:
        """Route based on mesh configuration"""
        # Find matching virtual service
        for vs_name, vs_config in self.virtual_services.items():
            if self.matches_virtual_service(request, vs_config):
                # Apply routing rules
                destination = self.apply_routing_rules(request, vs_config)
                
                # Apply destination rules
                if destination in self.destination_rules:
                    return self.apply_destination_rules(
                        destination,
                        self.destination_rules[destination]
                    )
                
                return self.get_service_endpoint(destination)
        
        # Default routing
        return self.get_service_endpoint(request['service'])
```

#### Multi-Region Discovery
```python
class MultiRegionDiscovery:
    """
    Service discovery across multiple regions
    """
    
    def __init__(self):
        self.regions = {}
        self.global_services = {}
        self.region_preferences = {}
        
    def register_region(self, region: str, registry_url: str):
        """Register a regional registry"""
        self.regions[region] = {
            'registry_url': registry_url,
            'latency': {},  # Latency to other regions
            'services': {}
        }
    
    def discover_global(self, service_name: str, 
                       client_region: str) -> List[dict]:
        """Discover service globally with region preference"""
        all_instances = []
        
        # Collect from all regions
        for region, config in self.regions.items():
            try:
                instances = self.query_region(region, service_name)
                for instance in instances:
                    instance['region'] = region
                    instance['latency'] = self.get_region_latency(
                        client_region, region
                    )
                all_instances.extend(instances)
            except:
                # Region might be down
                continue
        
        # Sort by preference (latency, health, load)
        return sorted(all_instances, key=lambda x: (
            x['latency'],
            0 if x.get('health') == 'healthy' else 1,
            x.get('load', 0)
        ))
    
    def implement_geo_routing(self, service_name: str, 
                            client_location: dict) -> dict:
        """Route to nearest healthy instance"""
        instances = self.discover_global(
            service_name,
            self.get_client_region(client_location)
        )
        
        # Filter by health and capacity
        available = [
            i for i in instances
            if i.get('health') == 'healthy' and 
               i.get('capacity_available', 100) > 10
        ]
        
        if available:
            return available[0]  # Nearest
        
        # Fallback to any healthy instance
        healthy = [i for i in instances if i.get('health') == 'healthy']
        if healthy:
            return healthy[0]
        
        raise Exception(f"No healthy instances found for {service_name}")
```

### Discovery Anti-Patterns

<div class="antipatterns">
<h3>⚠️ Common Service Discovery Mistakes</h3>

1. **No Cache Invalidation**
   ```python
   # BAD: Cache forever
   def get_service(name):
       if name in cache:
           return cache[name]  # Could be hours old!
   
   # GOOD: TTL and refresh
   def get_service(name):
       if name in cache and cache[name]['expires'] > time.time():
           return cache[name]['data']
       return refresh_cache(name)
   ```

2. **No Failure Handling**
   ```python
   # BAD: First failure kills everything
   instance = discover_service("api")
   return call_service(instance)  # What if instance is down?
   
   # GOOD: Retry with different instances
   instances = discover_service("api")
   for instance in instances[:3]:  # Try up to 3
       try:
           return call_service(instance)
       except:
           continue
   ```

3. **Synchronous Health Checks**
   ```python
   # BAD: Block on health checks
   def get_healthy_services():
       healthy = []
       for service in all_services:
           if check_health_sync(service):  # Blocks!
               healthy.append(service)
       return healthy
   
   # GOOD: Async health checks
   async def get_healthy_services():
       tasks = [check_health_async(s) for s in all_services]
       results = await asyncio.gather(*tasks)
       return [s for s, healthy in zip(all_services, results) if healthy]
   ```
</div>

---

## 🚀 Level 4: Expert

### Production Service Discovery Systems

#### Consul Service Discovery
```python
import consul

class ConsulServiceDiscovery:
    """
    HashiCorp Consul integration
    """
    
    def __init__(self, consul_host='localhost', consul_port=8500):
        self.consul = consul.Consul(host=consul_host, port=consul_port)
        self.watched_services = {}
        
    def register_service(self, 
                        name: str,
                        service_id: str,
                        address: str,
                        port: int,
                        tags: List[str] = None,
                        check: dict = None):
        """Register service with Consul"""
        # Define health check
        if not check:
            check = consul.Check.http(
                f"http://{address}:{port}/health",
                interval="30s",
                timeout="3s"
            )
        
        # Register
        self.consul.agent.service.register(
            name=name,
            service_id=service_id,
            address=address,
            port=port,
            tags=tags or [],
            check=check
        )
    
    def discover_service(self, service_name: str, 
                        tag: str = None,
                        passing_only: bool = True) -> List[dict]:
        """Discover service instances"""
        # Query Consul
        _, services = self.consul.health.service(
            service_name,
            tag=tag,
            passing=passing_only
        )
        
        instances = []
        for service in services:
            instances.append({
                'id': service['Service']['ID'],
                'address': service['Service']['Address'],
                'port': service['Service']['Port'],
                'tags': service['Service']['Tags'],
                'datacenter': service['Node']['Datacenter'],
                'health': 'healthy' if passing_only else service['Checks'][0]['Status']
            })
        
        return instances
    
    def watch_service(self, service_name: str, callback):
        """Watch for service changes"""
        index = None
        
        def watch_loop():
            nonlocal index
            while True:
                try:
                    # Blocking query
                    index, services = self.consul.health.service(
                        service_name,
                        index=index,
                        wait='30s'
                    )
                    
                    # Notify callback of changes
                    callback(services)
                    
                except Exception as e:
                    print(f"Watch error: {e}")
                    time.sleep(5)
        
        # Start watch in background
        thread = threading.Thread(target=watch_loop)
        thread.daemon = True
        thread.start()
        
        self.watched_services[service_name] = thread
    
    def create_prepared_query(self, name: str, service: str, 
                            near: str = "_agent",
                            tags: List[str] = None):
        """Create prepared query for geo-aware discovery"""
        query = {
            "Name": name,
            "Service": {
                "Service": service,
                "Tags": tags or [],
                "Near": near,  # Sort by network distance
                "OnlyPassing": True
            }
        }
        
        return self.consul.query.create(query)
```

#### Kubernetes Service Discovery
```python
from kubernetes import client, config, watch

class KubernetesServiceDiscovery:
    """
    Kubernetes native service discovery
    """
    
    def __init__(self):
        # Load config from pod or kubeconfig
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
        
        self.v1 = client.CoreV1Api()
        self.namespace = "default"
        
    def discover_service_endpoints(self, service_name: str) -> List[dict]:
        """Discover endpoints for a service"""
        try:
            # Get service
            service = self.v1.read_namespaced_service(
                name=service_name,
                namespace=self.namespace
            )
            
            # Get endpoints
            endpoints = self.v1.read_namespaced_endpoints(
                name=service_name,
                namespace=self.namespace
            )
            
            instances = []
            for subset in endpoints.subsets:
                for address in subset.addresses:
                    for port in subset.ports:
                        instances.append({
                            'ip': address.ip,
                            'port': port.port,
                            'protocol': port.protocol,
                            'ready': True,
                            'pod_name': address.target_ref.name if address.target_ref else None
                        })
            
            return instances
            
        except client.exceptions.ApiException as e:
            print(f"Service discovery failed: {e}")
            return []
    
    def discover_by_label(self, label_selector: str) -> List[dict]:
        """Discover pods by label selector"""
        pods = self.v1.list_namespaced_pod(
            namespace=self.namespace,
            label_selector=label_selector
        )
        
        instances = []
        for pod in pods.items:
            if pod.status.phase == "Running":
                instances.append({
                    'name': pod.metadata.name,
                    'ip': pod.status.pod_ip,
                    'labels': pod.metadata.labels,
                    'containers': [c.name for c in pod.spec.containers]
                })
        
        return instances
    
    def watch_service_changes(self, service_name: str, callback):
        """Watch for service endpoint changes"""
        w = watch.Watch()
        
        for event in w.stream(
            self.v1.list_namespaced_endpoints,
            namespace=self.namespace,
            field_selector=f"metadata.name={service_name}"
        ):
            event_type = event['type']  # ADDED, MODIFIED, DELETED
            endpoints = event['object']
            
            # Extract instances
            instances = []
            for subset in endpoints.subsets:
                for address in subset.addresses:
                    instances.append({
                        'ip': address.ip,
                        'ready': True
                    })
            
            callback(event_type, instances)
```

### Real-World Case Study: Netflix Eureka

```python
class EurekaServiceDiscovery:
    """
    Netflix Eureka-style service discovery
    """
    
    def __init__(self, eureka_url: str):
        self.eureka_url = eureka_url
        self.instance_id = self.generate_instance_id()
        self.heartbeat_interval = 30
        
    def register(self, app_name: str, **kwargs):
        """Register with Eureka"""
        instance = {
            "instance": {
                "instanceId": self.instance_id,
                "app": app_name.upper(),
                "hostName": kwargs.get('hostname', socket.gethostname()),
                "ipAddr": kwargs.get('ip', self.get_ip_address()),
                "status": "UP",
                "port": {
                    "$": kwargs.get('port', 8080),
                    "@enabled": "true"
                },
                "vipAddress": app_name.lower(),
                "dataCenterInfo": {
                    "@class": "com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo",
                    "name": "MyOwn"
                },
                "leaseInfo": {
                    "renewalIntervalInSecs": self.heartbeat_interval,
                    "durationInSecs": 90
                }
            }
        }
        
        # Register
        response = requests.post(
            f"{self.eureka_url}/eureka/apps/{app_name.upper()}",
            json=instance,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 204:
            # Start heartbeat
            self.start_heartbeat(app_name)
            return True
        
        return False
    
    def start_heartbeat(self, app_name: str):
        """Send periodic heartbeats"""
        def heartbeat_loop():
            while True:
                try:
                    response = requests.put(
                        f"{self.eureka_url}/eureka/apps/{app_name.upper()}/{self.instance_id}"
                    )
                    if response.status_code != 200:
                        print(f"Heartbeat failed: {response.status_code}")
                except Exception as e:
                    print(f"Heartbeat error: {e}")
                
                time.sleep(self.heartbeat_interval)
        
        thread = threading.Thread(target=heartbeat_loop)
        thread.daemon = True
        thread.start()
    
    def discover(self, app_name: str) -> List[dict]:
        """Discover service instances"""
        response = requests.get(
            f"{self.eureka_url}/eureka/apps/{app_name.upper()}",
            headers={"Accept": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            instances = []
            
            app = data.get('application', {})
            for instance in app.get('instance', []):
                if instance['status'] == 'UP':
                    instances.append({
                        'instanceId': instance['instanceId'],
                        'hostname': instance['hostName'],
                        'ip': instance['ipAddr'],
                        'port': instance['port']['$'],
                        'vip': instance['vipAddress'],
                        'metadata': instance.get('metadata', {})
                    })
            
            return instances
        
        return []
```

---

## 🎯 Level 5: Mastery

### Theoretical Foundations

```python
class OptimalServiceDiscovery:
    """
    Theoretically optimal service discovery
    """
    
    def __init__(self):
        self.services = {}
        self.network_topology = NetworkTopology()
        self.failure_detector = PhiAccrualFailureDetector()
        
    def calculate_discovery_overhead(self, 
                                   num_services: int,
                                   num_instances: int,
                                   query_rate: float) -> dict:
        """
        Calculate theoretical overhead of discovery
        """
        # Gossip protocol overhead
        gossip_overhead = num_services * num_instances * math.log(num_instances)
        
        # Consensus protocol overhead (Raft/Paxos)
        consensus_overhead = num_services * num_instances * (num_instances - 1)
        
        # Client-side caching benefit
        cache_hit_rate = 0.9  # Typical
        effective_query_rate = query_rate * (1 - cache_hit_rate)
        
        return {
            'gossip_bandwidth': gossip_overhead * 64,  # bytes/sec
            'consensus_bandwidth': consensus_overhead * 128,
            'registry_load': effective_query_rate,
            'client_memory': num_services * num_instances * 256  # bytes
        }
    
    def implement_bloom_filter_discovery(self):
        """
        Use Bloom filters for efficient discovery
        """
        from pybloom_live import BloomFilter
        
        # Create Bloom filter for each service
        self.bloom_filters = {}
        
        for service_name, instances in self.services.items():
            # Size for ~1% false positive rate
            bf = BloomFilter(capacity=len(instances) * 10, error_rate=0.01)
            
            for instance in instances:
                # Add instance attributes to filter
                bf.add(f"{instance['ip']}:{instance['port']}")
                for tag in instance.get('tags', []):
                    bf.add(f"{service_name}:{tag}")
            
            self.bloom_filters[service_name] = bf
        
        return self.bloom_filters
```

### Future Directions

1. **ML-Driven Discovery**: Predict service locations before lookup
2. **Blockchain Registry**: Decentralized service registry
3. **Zero-Knowledge Discovery**: Find services without revealing identity
4. **Quantum Service Mesh**: Leverage quantum entanglement for instant discovery

---

## 📋 Quick Reference

### Discovery Method Selection

| Scenario | Recommended Method | Why |
|----------|-------------------|-----|
| Kubernetes cluster | Native K8s DNS/API | Built-in integration |
| Multi-cloud | Consul/Istio | Cloud agnostic |
| Simple microservices | Eureka/Consul | Easy setup |
| Large scale | Custom with caching | Performance |
| Cross-region | Multi-registry federation | Locality awareness |

### Implementation Checklist

- [ ] Choose discovery method (client/server/DNS)
- [ ] Implement health checking
- [ ] Add caching with TTL
- [ ] Handle discovery failures
- [ ] Monitor registry performance
- [ ] Document service naming conventions
- [ ] Test with service churn
- [ ] Plan for registry failure

---

<div class="navigation-footer">
<div class="pattern-relationships">
<h3>🔗 Related Patterns & Concepts</h3>

**🤝 Complementary Patterns**:
- [Load Balancing](/patterns/load-balancing/) - Use discovered services
- [Health Check](/patterns/health-check/) - Validate service health
- [Circuit Breaker](/patterns/circuit-breaker/) - Handle failures

**🧠 Foundational Concepts**:
- [Axiom 3: Failure](/part1-axioms/axiom3-failure/) - Services come and go
- [Axiom 5: Coordination](/part1-axioms/axiom5-coordination/) - Registry coordination
</div>
</div>

---

*"In distributed systems, finding a service is half the battle—the other half is finding it healthy."*