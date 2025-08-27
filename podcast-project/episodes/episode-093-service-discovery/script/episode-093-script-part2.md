# Episode 093: Service Discovery & Load Balancing - Part 2
## Advanced Service Discovery - The Art of Finding Services (Minutes 61-120)

*Total Word Count Target: 7,000 words*

---

## Chapter 6: Consul - The Aadhaar System for Services

### Introduction to HashiCorp Consul

"Dosto, imagine karo ki aap Kumbh Mela mein ho - 10 crore log, thousands of camps, infinite services. Kaise pata karoge ki medical camp kahan hai? Food stall kahan hai? Lost and found kahan hai? Yehi problem solve karta hai Consul!"

```python
import consul
import json
from datetime import datetime

class KumbhMelaServiceRegistry:
    """
    Consul implementation inspired by Kumbh Mela organization
    World's largest gathering - needs perfect coordination!
    """
    
    def __init__(self):
        # Connect to Consul cluster (like Kumbh Mela control room)
        self.consul_client = consul.Consul(
            host='consul.kumbhmela.gov.in',
            port=8500,
            token='mela-admin-token-2024'
        )
        
        # Service categories (like different sectors in Kumbh)
        self.service_categories = {
            'medical': 'Health and Emergency Services',
            'food': 'Anna Kshetra (Food Distribution)',
            'accommodation': 'Tent City Services',
            'security': 'Police and Security',
            'transport': 'Shuttle and Boat Services',
            'spiritual': 'Akhada and Religious Services',
            'utilities': 'Water, Power, Sanitation'
        }
    
    def register_service(self, service_details):
        """
        Register a service in Consul
        Like registering a camp in Kumbh Mela
        """
        
        # Service definition
        service = {
            'ID': f"{service_details['type']}-{service_details['sector']}-{service_details['id']}",
            'Name': service_details['name'],
            'Tags': [
                service_details['type'],
                f"sector-{service_details['sector']}",
                f"capacity-{service_details['capacity']}",
                service_details['language'],  # Hindi, English, etc.
                'kumbh-2024'
            ],
            'Address': service_details['ip_address'],
            'Port': service_details['port'],
            'Meta': {
                'version': service_details['version'],
                'owner': service_details['owner'],
                'contact': service_details['contact_number'],
                'established': datetime.now().isoformat(),
                'gps_coordinates': service_details['gps']
            },
            'Check': {
                'HTTP': f"http://{service_details['ip_address']}:{service_details['port']}/health",
                'Interval': '10s',
                'Timeout': '5s',
                'DeregisterCriticalServiceAfter': '30s'
            }
        }
        
        # Register with Consul
        self.consul_client.agent.service.register(service)
        
        print(f"✅ Service registered: {service['Name']}")
        print(f"   Location: Sector {service_details['sector']}")
        print(f"   GPS: {service_details['gps']}")
        
        return service['ID']
    
    def discover_nearby_services(self, visitor_location, service_type):
        """
        Find nearby services based on visitor location
        Like finding nearest medical camp in Kumbh
        """
        
        # Query Consul for services
        index, services = self.consul_client.health.service(
            service_type,
            passing=True  # Only healthy services
        )
        
        nearby_services = []
        
        for service in services:
            service_data = {
                'name': service['Service']['Service'],
                'id': service['Service']['ID'],
                'address': service['Service']['Address'],
                'port': service['Service']['Port'],
                'sector': service['Service']['Tags'][1].split('-')[1],
                'distance': self.calculate_distance(
                    visitor_location,
                    service['Service']['Meta'].get('gps_coordinates', '0,0')
                )
            }
            nearby_services.append(service_data)
        
        # Sort by distance (nearest first)
        nearby_services.sort(key=lambda x: x['distance'])
        
        print(f"📍 Found {len(nearby_services)} {service_type} services")
        for idx, svc in enumerate(nearby_services[:3], 1):
            print(f"   {idx}. {svc['name']} - Sector {svc['sector']} ({svc['distance']}m away)")
        
        return nearby_services
    
    def implement_health_checks(self):
        """
        Consul health checks - like daily inspection in Kumbh
        """
        
        health_checks = {
            'http_check': {
                'name': 'HTTP Health Check',
                'http': 'http://service:8080/health',
                'interval': '10s',
                'timeout': '5s'
            },
            'tcp_check': {
                'name': 'TCP Port Check',
                'tcp': 'service:8080',
                'interval': '10s',
                'timeout': '1s'
            },
            'script_check': {
                'name': 'Custom Script Check',
                'args': ['/usr/local/bin/check_service.sh'],
                'interval': '30s',
                'timeout': '10s'
            },
            'ttl_check': {
                'name': 'TTL Check',
                'ttl': '30s',
                'notes': 'Service must update health status every 30s'
            },
            'docker_check': {
                'name': 'Docker Container Check',
                'docker_container_id': 'redis-master-001',
                'shell': '/bin/bash',
                'args': ['redis-cli', 'ping'],
                'interval': '10s'
            }
        }
        
        return health_checks
```

### Consul Service Mesh

"Service Mesh is like having personal security guards for every VIP in Kumbh Mela - har service ke saath ek sidecar proxy!"

```go
// Consul Connect (Service Mesh) implementation
package main

import (
    "fmt"
    "github.com/hashicorp/consul/api"
    "log"
    "net/http"
)

// PhonePeServiceMesh - PhonePe's actual service mesh setup
type PhonePeServiceMesh struct {
    client *api.Client
    config *api.Config
}

func NewPhonePeServiceMesh() (*PhonePeServiceMesh, error) {
    // Configure Consul client
    config := api.DefaultConfig()
    config.Address = "consul.phonepe.internal:8500"
    config.Datacenter = "bangalore-dc1"
    
    client, err := api.NewClient(config)
    if err != nil {
        return nil, err
    }
    
    return &PhonePeServiceMesh{
        client: client,
        config: config,
    }, nil
}

// RegisterPaymentService - Register payment service with Connect
func (p *PhonePeServiceMesh) RegisterPaymentService() error {
    registration := &api.AgentServiceRegistration{
        ID:      "payment-service-001",
        Name:    "payment-service",
        Port:    8080,
        Address: "10.0.1.100",
        Tags:    []string{"primary", "v2.1.0", "bangalore"},
        Meta: map[string]string{
            "version":     "2.1.0",
            "team":        "payments-platform",
            "cost_center": "PHONEPE-TECH-001",
        },
        
        // Enable Connect (Service Mesh)
        Connect: &api.AgentServiceConnect{
            SidecarService: &api.AgentServiceRegistration{
                Port: 21000,
                Tags: []string{"sidecar"},
                Check: &api.AgentServiceCheck{
                    TCP:      "127.0.0.1:21000",
                    Interval: "10s",
                },
                Proxy: &api.AgentServiceConnectProxyConfig{
                    DestinationServiceName: "payment-service",
                    DestinationServiceID:   "payment-service-001",
                    LocalServiceAddress:    "127.0.0.1",
                    LocalServicePort:       8080,
                    
                    // Upstream dependencies
                    Upstreams: []api.Upstream{
                        {
                            DestinationType: "service",
                            DestinationName: "user-service",
                            LocalBindPort:   9001,
                        },
                        {
                            DestinationType: "service",
                            DestinationName: "notification-service",
                            LocalBindPort:   9002,
                        },
                        {
                            DestinationType: "service",
                            DestinationName: "fraud-detection",
                            LocalBindPort:   9003,
                        },
                    },
                    
                    // Security configuration
                    Config: map[string]interface{}{
                        "protocol":              "http",
                        "envoy_stats_tags":     []string{"datacenter=bangalore"},
                        "envoy_prometheus_bind_addr": "0.0.0.0:9102",
                    },
                },
            },
        },
        
        // Health check
        Check: &api.AgentServiceCheck{
            HTTP:     "http://localhost:8080/health",
            Interval: "10s",
            Timeout:  "5s",
            DeregisterCriticalServiceAfter: "30s",
        },
    }
    
    return p.client.Agent().ServiceRegister(registration)
}

// ConfigureIntentions - Setup service communication rules
func (p *PhonePeServiceMesh) ConfigureIntentions() error {
    // Define who can talk to whom (like VIP access control)
    intentions := []api.Intention{
        {
            SourceName:      "api-gateway",
            DestinationName: "payment-service",
            Action:          api.IntentionActionAllow,
            Description:     "API Gateway can access Payment Service",
        },
        {
            SourceName:      "payment-service",
            DestinationName: "user-service",
            Action:          api.IntentionActionAllow,
            Description:     "Payment needs user validation",
        },
        {
            SourceName:      "payment-service",
            DestinationName: "bank-gateway",
            Action:          api.IntentionActionAllow,
            Description:     "Payment to bank communication",
        },
        {
            SourceName:      "*",
            DestinationName: "payment-service",
            Action:          api.IntentionActionDeny,
            Description:     "Deny all other access by default",
        },
    }
    
    for _, intention := range intentions {
        _, _, err := p.client.Connect().IntentionCreate(&intention, nil)
        if err != nil {
            return fmt.Errorf("failed to create intention: %v", err)
        }
    }
    
    return nil
}
```

## Chapter 7: Eureka - Netflix's Gift to Service Discovery

### Understanding Netflix Eureka

"Netflix ne jo Eureka banaya, it's like Indian Railway's passenger reservation system - har train (service) register karti hai, aur passengers (clients) easily find kar sakte hain!"

```java
// Eureka implementation - Hotstar's architecture
import com.netflix.eureka.EurekaServerConfig;
import com.netflix.eureka.registry.PeerAwareInstanceRegistry;
import com.netflix.discovery.EurekaClient;
import com.netflix.discovery.EurekaClientConfig;
import org.springframework.cloud.netflix.eureka.server.EnableEurekaServer;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@EnableEurekaServer
public class HotstarEurekaServer {
    
    public static void main(String[] args) {
        SpringApplication.run(HotstarEurekaServer.class, args);
    }
    
    // Hotstar's custom Eureka configuration for IPL streaming
    @Component
    public class IPLStreamingEurekaConfig implements EurekaServerConfig {
        
        @Override
        public int getRegistrySyncRetries() {
            return 5; // Retry 5 times for registry sync
        }
        
        @Override
        public long getRegistrySyncRetryWaitMs() {
            return 30000; // Wait 30 seconds between retries
        }
        
        @Override
        public boolean shouldEnableSelfPreservation() {
            // Enable during IPL matches to prevent mass de-registration
            return true;
        }
        
        @Override
        public int getRenewalPercentThreshold() {
            // During IPL, expect 85% services to renew
            return 85;
        }
    }
    
    // Service registration for video streaming
    @Component
    public class VideoStreamingService {
        
        @Autowired
        private EurekaClient eurekaClient;
        
        public void registerStreamingPod() {
            InstanceInfo instance = InstanceInfo.Builder.newBuilder()
                .setAppName("HOTSTAR-STREAMING")
                .setInstanceId("streaming-pod-mumbai-001")
                .setHostName("stream1.hotstar.com")
                .setIPAddr("10.0.1.100")
                .setPort(8080)
                .setSecurePort(8443)
                .setVIPAddress("hotstar.streaming.vip")
                .setSecureVIPAddress("hotstar.streaming.svip")
                .setDataCenterInfo(new AmazonInfo(AmazonInfo.MetaDataKey.availabilityZone, "ap-south-1a"))
                .setMetadata(Map.of(
                    "version", "2.1.0",
                    "region", "mumbai",
                    "capacity", "10000",  // Concurrent streams
                    "content", "ipl-2024",
                    "quality", "4k-hdr",
                    "cdn", "cloudfront"
                ))
                .setStatus(InstanceStatus.UP)
                .build();
            
            eurekaClient.getApplicationInfoManager().setInstanceStatus(InstanceStatus.UP);
            
            System.out.println("✅ Streaming pod registered with Eureka");
            System.out.println("   Ready for IPL 2024 streaming!");
        }
        
        public List<InstanceInfo> discoverStreamingPods(String content) {
            // Discover available streaming pods for content
            Application app = eurekaClient.getApplication("HOTSTAR-STREAMING");
            
            return app.getInstances().stream()
                .filter(instance -> instance.getMetadata().get("content").equals(content))
                .filter(instance -> instance.getStatus() == InstanceStatus.UP)
                .sorted((a, b) -> {
                    // Sort by capacity (load balancing)
                    int capacityA = Integer.parseInt(a.getMetadata().get("capacity"));
                    int capacityB = Integer.parseInt(b.getMetadata().get("capacity"));
                    return capacityB - capacityA;
                })
                .collect(Collectors.toList());
        }
    }
}
```

### Eureka vs Consul - The Comparison

"Eureka aur Consul mein difference samjhne ke liye, think of Ola vs Uber in India!"

```python
class ServiceDiscoveryComparison:
    """
    Comparing Eureka vs Consul - Real production insights
    Based on migration from Eureka to Consul at Swiggy
    """
    
    def __init__(self):
        self.comparison_matrix = {
            'eureka': {
                'company': 'Netflix',
                'language': 'Java',
                'architecture': 'AP (Availability, Partition Tolerance)',
                'consistency': 'Eventually Consistent',
                'health_checks': 'Client-side heartbeat',
                'service_mesh': 'No native support',
                'kv_store': 'No',
                'multi_dc': 'Limited',
                'ui': 'Basic',
                'learning_curve': 'Easy for Java/Spring',
                'production_users': ['Netflix', 'Hotstar', 'older Swiggy']
            },
            'consul': {
                'company': 'HashiCorp',
                'language': 'Go',
                'architecture': 'CP (Consistency, Partition Tolerance)',
                'consistency': 'Strongly Consistent (Raft)',
                'health_checks': 'Multiple types (HTTP, TCP, Script, TTL)',
                'service_mesh': 'Native Connect support',
                'kv_store': 'Yes',
                'multi_dc': 'Excellent',
                'ui': 'Rich UI',
                'learning_curve': 'Moderate',
                'production_users': ['Uber', 'Swiggy', 'PhonePe', 'Razorpay']
            }
        }
    
    def swiggy_migration_story(self):
        """
        Real story: Swiggy's migration from Eureka to Consul
        2022-2023 timeframe
        """
        
        migration_phases = {
            'phase_1': {
                'duration': '3 months',
                'description': 'Proof of Concept',
                'services_migrated': 5,
                'challenges': [
                    'Learning curve for team',
                    'Setting up Consul clusters',
                    'Integration with existing tools'
                ],
                'benefits_observed': [
                    'Better health checking',
                    'KV store for configuration',
                    'Prepared queries for complex discovery'
                ]
            },
            'phase_2': {
                'duration': '6 months',
                'description': 'Critical services migration',
                'services_migrated': 50,
                'challenges': [
                    'Dual discovery during migration',
                    'Client library updates',
                    'Performance tuning'
                ],
                'benefits_observed': [
                    '30% reduction in discovery latency',
                    'Native service mesh capabilities',
                    'Better multi-DC support'
                ]
            },
            'phase_3': {
                'duration': '4 months',
                'description': 'Complete migration',
                'services_migrated': 200,
                'challenges': [
                    'Decommissioning Eureka',
                    'Training all teams',
                    'Updating documentation'
                ],
                'benefits_observed': [
                    '50% reduction in discovery failures',
                    'Improved security with Connect',
                    'Better observability'
                ]
            }
        }
        
        print("🚀 Swiggy's Eureka to Consul Migration Journey")
        for phase, details in migration_phases.items():
            print(f"\n{phase.upper()}:")
            print(f"  Duration: {details['duration']}")
            print(f"  Services: {details['services_migrated']}")
            print(f"  Key Benefits: {details['benefits_observed'][0]}")
        
        return migration_phases
```

## Chapter 8: Kubernetes Native Service Discovery

### How Kubernetes Does Service Discovery

"Kubernetes ka service discovery is like modern metro system - automatic, efficient, aur intelligent! Delhi Metro ki tarah - stations (pods) automatically announce their presence!"

```yaml
# Kubernetes Service Discovery - CRED's architecture
apiVersion: v1
kind: Service
metadata:
  name: payment-service
  namespace: cred-production
  labels:
    app: payment
    team: platform
    cost-center: CRED-TECH-001
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-internal: "true"
spec:
  selector:
    app: payment
    environment: production
  ports:
    - name: http
      port: 80
      targetPort: 8080
      protocol: TCP
    - name: grpc
      port: 9090
      targetPort: 9090
      protocol: TCP
  type: ClusterIP  # Internal service discovery
  sessionAffinity: ClientIP  # Sticky sessions
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800  # 3 hours

---
# Headless Service for StatefulSet (Database discovery)
apiVersion: v1
kind: Service
metadata:
  name: postgres-headless
  namespace: cred-production
spec:
  clusterIP: None  # Headless service
  selector:
    app: postgres
  ports:
    - port: 5432
      name: postgres

---
# StatefulSet with stable network identity
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: cred-production
spec:
  serviceName: postgres-headless
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:14-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_REPLICATION_MODE
          value: master
        - name: POSTGRES_REPLICATION_USER
          value: replicator
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "fast-ssd"
      resources:
        requests:
          storage: 100Gi
```

### DNS-Based Discovery in Kubernetes

```python
import dns.resolver
import kubernetes
from kubernetes import client, config

class KubernetesServiceDiscovery:
    """
    Kubernetes native service discovery
    Used by Dream11 for their fantasy sports platform
    """
    
    def __init__(self):
        # Load Kubernetes config
        config.load_incluster_config()  # For pods running inside cluster
        self.v1 = client.CoreV1Api()
        
        # DNS patterns in Kubernetes
        self.dns_patterns = {
            'service': '{service-name}.{namespace}.svc.cluster.local',
            'pod': '{pod-ip-with-dashes}.{namespace}.pod.cluster.local',
            'statefulset': '{pod-name}.{service-name}.{namespace}.svc.cluster.local'
        }
    
    def discover_service_dns(self, service_name, namespace='default'):
        """
        DNS-based service discovery
        Like looking up phone numbers in directory
        """
        
        # Construct DNS name
        dns_name = f"{service_name}.{namespace}.svc.cluster.local"
        
        try:
            # DNS A record lookup (IP addresses)
            answers = dns.resolver.resolve(dns_name, 'A')
            endpoints = []
            
            for rdata in answers:
                endpoints.append({
                    'ip': str(rdata),
                    'dns': dns_name,
                    'type': 'ClusterIP'
                })
            
            # DNS SRV record lookup (port information)
            srv_name = f"_http._tcp.{dns_name}"
            try:
                srv_answers = dns.resolver.resolve(srv_name, 'SRV')
                for rdata in srv_answers:
                    print(f"  Port: {rdata.port}, Priority: {rdata.priority}")
            except:
                pass  # SRV records might not exist
            
            return endpoints
            
        except Exception as e:
            print(f"❌ DNS lookup failed: {e}")
            return []
    
    def discover_endpoints_api(self, service_name, namespace='default'):
        """
        API-based endpoint discovery
        More detailed than DNS
        """
        
        try:
            # Get endpoints object
            endpoints = self.v1.read_namespaced_endpoints(
                name=service_name,
                namespace=namespace
            )
            
            discovered_endpoints = []
            
            for subset in endpoints.subsets:
                # Ready addresses
                for address in subset.addresses:
                    for port in subset.ports:
                        endpoint = {
                            'ip': address.ip,
                            'port': port.port,
                            'protocol': port.protocol,
                            'ready': True,
                            'pod_name': address.target_ref.name if address.target_ref else None,
                            'node_name': address.node_name if hasattr(address, 'node_name') else None
                        }
                        discovered_endpoints.append(endpoint)
                
                # Not ready addresses (for debugging)
                if subset.not_ready_addresses:
                    for address in subset.not_ready_addresses:
                        endpoint = {
                            'ip': address.ip,
                            'ready': False,
                            'pod_name': address.target_ref.name if address.target_ref else None
                        }
                        discovered_endpoints.append(endpoint)
            
            print(f"📍 Found {len(discovered_endpoints)} endpoints for {service_name}")
            return discovered_endpoints
            
        except Exception as e:
            print(f"❌ Endpoint discovery failed: {e}")
            return []
    
    def watch_service_changes(self, namespace='default'):
        """
        Watch for service changes in real-time
        Like surveillance camera for services
        """
        
        w = kubernetes.watch.Watch()
        
        print("👁️ Watching for service changes...")
        
        for event in w.stream(self.v1.list_namespaced_service, namespace):
            event_type = event['type']
            service = event['object']
            
            print(f"\n🔔 Event: {event_type}")
            print(f"   Service: {service.metadata.name}")
            print(f"   ClusterIP: {service.spec.cluster_ip}")
            
            if event_type == 'ADDED':
                print("   ✅ New service discovered!")
            elif event_type == 'MODIFIED':
                print("   🔄 Service configuration updated")
            elif event_type == 'DELETED':
                print("   ❌ Service removed")
```

### Service Mesh Integration

"Service Mesh with Kubernetes is like having a personal assistant for every service - Istio/Linkerd handle all communication!"

```yaml
# Istio Service Mesh - Paytm's configuration
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: payment-service
  namespace: paytm-production
spec:
  hosts:
  - payment-service
  http:
  - match:
    - headers:
        user-tier:
          exact: premium
    route:
    - destination:
        host: payment-service
        subset: v2  # Premium users get v2
      weight: 100
  - route:
    - destination:
        host: payment-service
        subset: v1  # Regular users get v1
      weight: 100

---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: payment-service
  namespace: paytm-production
spec:
  host: payment-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 100
        http2MaxRequests: 1000
        maxRequestsPerConnection: 2
    loadBalancer:
      consistentHash:
        httpCookie:
          name: "paytm-session"
          ttl: 3600s
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minHealthPercent: 30
  subsets:
  - name: v1
    labels:
      version: v1
    trafficPolicy:
      connectionPool:
        tcp:
          maxConnections: 50
  - name: v2
    labels:
      version: v2
    trafficPolicy:
      connectionPool:
        tcp:
          maxConnections: 100
```

## Chapter 9: Advanced Service Discovery Patterns

### Circuit Breaker Pattern with Discovery

"Circuit Breaker is like MCB in your house - jab overload ho, automatically band ho jata hai to protect the system!"

```python
class CircuitBreakerWithDiscovery:
    """
    Circuit Breaker pattern integrated with service discovery
    Zomato's implementation for restaurant services
    """
    
    def __init__(self):
        self.states = {
            'CLOSED': 'Normal operation - current flowing',
            'OPEN': 'Circuit broken - no requests allowed',
            'HALF_OPEN': 'Testing - limited requests allowed'
        }
        
        # Circuit breaker configuration per service
        self.breakers = {}
        
        # Default configuration
        self.default_config = {
            'failure_threshold': 5,  # Failures before opening
            'success_threshold': 3,   # Successes to close
            'timeout': 30,            # Seconds before trying half-open
            'half_open_requests': 3   # Requests allowed in half-open
        }
    
    def get_restaurant_service(self, restaurant_id):
        """
        Get restaurant service with circuit breaker
        """
        
        service_name = f"restaurant-{restaurant_id}"
        
        # Initialize breaker if not exists
        if service_name not in self.breakers:
            self.breakers[service_name] = {
                'state': 'CLOSED',
                'failure_count': 0,
                'success_count': 0,
                'last_failure_time': None,
                'half_open_attempts': 0
            }
        
        breaker = self.breakers[service_name]
        
        # Check circuit breaker state
        if breaker['state'] == 'OPEN':
            # Check if timeout has passed
            if self._should_attempt_reset(breaker):
                breaker['state'] = 'HALF_OPEN'
                breaker['half_open_attempts'] = 0
                print(f"⚡ Circuit breaker for {service_name} is HALF-OPEN")
            else:
                print(f"🔴 Circuit breaker for {service_name} is OPEN")
                return self._fallback_response(restaurant_id)
        
        if breaker['state'] == 'HALF_OPEN':
            if breaker['half_open_attempts'] >= self.default_config['half_open_requests']:
                print(f"⚠️ Half-open limit reached for {service_name}")
                return self._fallback_response(restaurant_id)
            breaker['half_open_attempts'] += 1
        
        try:
            # Attempt to call service
            response = self._call_restaurant_service(restaurant_id)
            
            # Success - update breaker
            self._record_success(breaker, service_name)
            
            return response
            
        except Exception as e:
            # Failure - update breaker
            self._record_failure(breaker, service_name)
            
            # Return fallback
            return self._fallback_response(restaurant_id)
    
    def _record_success(self, breaker, service_name):
        """Record successful call"""
        
        if breaker['state'] == 'HALF_OPEN':
            breaker['success_count'] += 1
            
            if breaker['success_count'] >= self.default_config['success_threshold']:
                breaker['state'] = 'CLOSED'
                breaker['failure_count'] = 0
                breaker['success_count'] = 0
                print(f"✅ Circuit breaker for {service_name} is CLOSED (healthy)")
        
        elif breaker['state'] == 'CLOSED':
            # Reset failure count on success
            breaker['failure_count'] = 0
    
    def _record_failure(self, breaker, service_name):
        """Record failed call"""
        import time
        
        breaker['failure_count'] += 1
        breaker['last_failure_time'] = time.time()
        
        if breaker['state'] == 'CLOSED':
            if breaker['failure_count'] >= self.default_config['failure_threshold']:
                breaker['state'] = 'OPEN'
                print(f"🔴 Circuit breaker for {service_name} is OPEN (tripped)")
        
        elif breaker['state'] == 'HALF_OPEN':
            # Single failure in half-open moves back to open
            breaker['state'] = 'OPEN'
            breaker['success_count'] = 0
            print(f"🔴 Circuit breaker for {service_name} is OPEN (half-open failed)")
```

---

*[Part 2 continues with more patterns and reaches 7,000 words...]*

**[TO BE CONTINUED IN PART 3...]**