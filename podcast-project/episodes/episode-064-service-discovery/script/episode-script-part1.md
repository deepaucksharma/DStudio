# Episode 64: Service Discovery - Mumbai ke Tiffin System se Seekho
## Part 1: Foundation aur Basic Patterns (0-60 Minutes)

---

### Opening Hook (0-3 Minutes)

Namaste doston! Aaj main aapko ek aisi story batane ja raha hu jo har Mumbai wale ki zindagi se judi hui hai. Socho, har din 2 lakh dabba-wallah Mumbai mein 5 lakh tiffin boxes deliver karte hain - bilkul perfect timing ke saath. Koi GPS nahi, koi fancy app nahi, phir bhi 99.99% accuracy!

Ab socho, agar yeh same precision aur efficiency hume apne microservices mein chahiye hoti hai, toh kya karenge? Answer hai - Service Discovery! Aur aaj ka episode exactly yahi sikhayega - how to build the tiffin delivery system of the digital world.

Lekin pehle main aapko ek real story batata hu. 2023 mein Swiggy ka traffic peak time pe 400% badh gaya - Diwali ke din. Unke system mein 1,200+ microservices the, har service multiple instances mein running thi. Ab imagine karo, ek single service ko dusre services ka address manually track karna pada hota. Disaster, right?

Exactly yahi problem solve karta hai Service Discovery. Aur Mumbai ke tiffin system se better analogy aur koi ho hi nahi sakti!

### Chapter 1: Service Discovery ki Zaroorat - The Evolution Story (3-15 Minutes)

#### Traditional Architecture ka Dukh

Bhai, 2010 ke time pe jab hum monolithic applications banate the, toh sab kuch simple tha. Ek hi server, ek hi database, ek hi IP address. Hardcode kar diya config file mein aur ho gaya!

```java
// Purane zamane ka jugaad - 2010 style
public class PaymentClient {
    private static final String PAYMENT_SERVICE_URL = "http://192.168.1.100:8080";
    private static final String DATABASE_URL = "jdbc:mysql://192.168.1.101:3306/payments";
    
    // Fixed IPs, fixed ports - life was simple!
    public PaymentResponse processPayment(PaymentRequest request) {
        RestTemplate restTemplate = new RestTemplate();
        return restTemplate.postForObject(PAYMENT_SERVICE_URL + "/pay", request, PaymentResponse.class);
    }
}
```

Lekin phir microservices ka zamana aaya. Suddenly, Paytm jaisi companies ke paas hundreds of services ho gayi:

- User Service
- Payment Service  
- Wallet Service
- KYC Service
- Notification Service
- Analytics Service
- Fraud Detection Service
- Merchant Service

Har service multiple instances mein run kar rahi thi. Auto-scaling on, containers migrate ho rahe the, regions change ho rahe the. Ab fixed IPs ka concept hi khatam!

#### The Mumbai Tiffin System Parallel

Mumbai ke dabba-wallah system mein dekho kaise coordination hota hai:

**1. Registration Phase**: Har naya dabba-wallah apna area, timing, aur capacity register karta hai central coordination system mein.

**2. Discovery Phase**: Jab customer ko tiffin chahiye, woh nearest available dabba-wallah find karta hai.

**3. Health Monitoring**: Agar koi dabba-wallah absent hai ya late hai, system automatically dusre options provide karta hai.

**4. Load Distribution**: High demand areas mein multiple dabba-wallah allocate karte hain.

Yahi exact same pattern follow karta hai modern service discovery!

#### Real Numbers - Scale ka Impact

PhonePe ka case study dekho:

**2020 mein PhonePe**:
- 50 microservices
- 200 service instances
- 5 regions
- Manual configuration files
- 2-3 hours deployment time
- 15 minute outage recovery

**2024 mein PhonePe**:
- 800+ microservices  
- 12,000+ service instances
- 12 regions across India
- Dynamic service discovery
- 5 minute deployment time
- 30 second outage recovery

Difference sirf technology ka nahi, approach ka hai!

### Chapter 2: Service Discovery Patterns Deep Dive (15-35 Minutes)

#### Pattern 1: Client-Side Discovery (Netflix Eureka Style)

Yeh pattern aise kaam karta hai jaise ek experienced dabba-wallah jo poora Mumbai ka map apne dimag mein rakhta hai.

```python
# Advanced client-side discovery implementation
import requests
import time
import random
from typing import List, Dict, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class ServiceInstance:
    """Service instance representation - Mumbai delivery point style"""
    host: str
    port: int
    region: str
    zone: str
    health_score: float
    latency_ms: int
    compliance_level: str  # For Indian regulatory requirements
    capacity_percentage: float
    
class MumbaiStyleServiceDiscovery:
    """Client-side service discovery inspired by Mumbai tiffin system"""
    
    def __init__(self, registry_url: str):
        self.registry_url = registry_url
        self.service_cache = {}
        self.health_cache = defaultdict(list)
        self.regional_preference = {
            "mumbai": ["mumbai", "pune", "nashik"],
            "delhi": ["delhi", "gurgaon", "noida"],
            "bangalore": ["bangalore", "mysore", "mangalore"],
            "hyderabad": ["hyderabad", "vijayawada", "warangal"]
        }
        
    def discover_service(self, service_name: str, user_region: str = "mumbai", 
                        compliance_required: bool = False) -> Optional[ServiceInstance]:
        """
        Main service discovery method - like finding best tiffin delivery route
        """
        # Step 1: Get all available instances
        instances = self._fetch_service_instances(service_name)
        if not instances:
            return None
            
        # Step 2: Filter by health
        healthy_instances = [inst for inst in instances if self._is_healthy(inst)]
        
        # Step 3: Filter by compliance if needed (RBI/IRDAI requirements)
        if compliance_required:
            healthy_instances = [inst for inst in healthy_instances 
                               if inst.compliance_level in ['rbi_certified', 'irdai_approved']]
        
        # Step 4: Regional preference (Mumbai tiffin wallah prefers local routes)
        preferred_instances = self._apply_regional_preference(healthy_instances, user_region)
        
        # Step 5: Load balancing with latency consideration
        return self._select_best_instance(preferred_instances)
    
    def _fetch_service_instances(self, service_name: str) -> List[ServiceInstance]:
        """Fetch instances from registry - like checking dabba-wallah availability"""
        try:
            response = requests.get(f"{self.registry_url}/services/{service_name}/instances", 
                                  timeout=2)
            if response.status_code == 200:
                instances_data = response.json()
                return [ServiceInstance(**inst) for inst in instances_data]
        except requests.RequestException as e:
            print(f"Registry access failed: {e}")
            # Fallback to cache
            return self.service_cache.get(service_name, [])
        
        return []
    
    def _is_healthy(self, instance: ServiceInstance) -> bool:
        """Health check - like checking if dabba-wallah is available and punctual"""
        # Recent health scores
        recent_scores = self.health_cache[f"{instance.host}:{instance.port}"][-10:]
        
        if not recent_scores:
            return instance.health_score > 0.8
            
        avg_recent_score = sum(recent_scores) / len(recent_scores)
        
        return (avg_recent_score > 0.7 and 
                instance.latency_ms < 500 and  # 500ms max for Indian networks
                instance.capacity_percentage < 90)  # Not overloaded
    
    def _apply_regional_preference(self, instances: List[ServiceInstance], 
                                 user_region: str) -> List[ServiceInstance]:
        """Regional routing - Mumbai traffic ke hisab se optimize"""
        if user_region not in self.regional_preference:
            return instances
            
        preferred_regions = self.regional_preference[user_region]
        
        # Sort by regional preference
        regional_instances = []
        for region in preferred_regions:
            region_instances = [inst for inst in instances if inst.region == region]
            regional_instances.extend(region_instances)
            
        # Add remaining instances
        remaining = [inst for inst in instances if inst.region not in preferred_regions]
        regional_instances.extend(remaining)
        
        return regional_instances
    
    def _select_best_instance(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        """Load balancing with Mumbai-style weighted selection"""
        if not instances:
            return None
            
        # Weighted selection based on performance metrics
        weights = []
        for instance in instances:
            # Weight calculation based on multiple factors
            latency_weight = max(0.1, 1.0 - (instance.latency_ms / 1000))
            capacity_weight = max(0.1, 1.0 - (instance.capacity_percentage / 100))
            health_weight = instance.health_score
            
            total_weight = (latency_weight * 0.4 + 
                          capacity_weight * 0.3 + 
                          health_weight * 0.3)
            weights.append(total_weight)
        
        # Weighted random selection
        total = sum(weights)
        if total == 0:
            return random.choice(instances)
            
        r = random.uniform(0, total)
        upto = 0
        for i, weight in enumerate(weights):
            if upto + weight >= r:
                return instances[i]
            upto += weight
            
        return instances[-1]  # Fallback
    
    def update_health_score(self, instance: ServiceInstance, success: bool, latency_ms: int):
        """Update health based on actual performance - like rating dabba-wallah"""
        key = f"{instance.host}:{instance.port}"
        
        if success:
            score = max(0.1, 1.0 - (latency_ms / 1000))
        else:
            score = 0.0
            
        self.health_cache[key].append(score)
        
        # Keep only recent 50 scores
        if len(self.health_cache[key]) > 50:
            self.health_cache[key] = self.health_cache[key][-50:]

# Usage example for Paytm-style payment service
def paytm_payment_example():
    """Real-world usage example"""
    discovery = MumbaiStyleServiceDiscovery("http://registry.paytm.internal:8080")
    
    # Discover payment service for UPI transaction
    payment_instance = discovery.discover_service(
        service_name="payment-processor-upi",
        user_region="mumbai",
        compliance_required=True  # RBI compliance needed
    )
    
    if payment_instance:
        print(f"Selected payment service: {payment_instance.host}:{payment_instance.port}")
        print(f"Region: {payment_instance.region}, Compliance: {payment_instance.compliance_level}")
        
        # Make actual API call
        start_time = time.time()
        try:
            # Simulated API call
            response = requests.post(
                f"http://{payment_instance.host}:{payment_instance.port}/process-payment",
                json={"amount": 1000, "type": "UPI"},
                timeout=5
            )
            
            end_time = time.time()
            latency = int((end_time - start_time) * 1000)
            
            # Update health score based on performance
            discovery.update_health_score(payment_instance, response.status_code == 200, latency)
            
        except requests.RequestException:
            discovery.update_health_score(payment_instance, False, 5000)
```

Yeh approach bilkul Mumbai ke senior dabba-wallah jaisi hai. Client ke paas pura control hai, woh decide karta hai kahan jaana hai.

**Client-Side Discovery ke Fayde**:
1. **Zero Network Hops**: Direct connection, no proxy overhead
2. **Custom Logic**: Apna load balancing algorithm implement kar sakte ho
3. **Regional Intelligence**: Mumbai traffic patterns ko consider kar sakte ho  
4. **Compliance Aware**: RBI/IRDAI rules easily handle kar sakte ho

**Nuksan**:
1. **Complex Client Libraries**: Har language mein sophisticated client banana padta hai
2. **Service Discovery Logic Duplication**: Har client mein same logic
3. **Updates Difficult**: Algorithm change karne ke liye sabko update karna padta hai

#### Pattern 2: Server-Side Discovery (Kubernetes/AWS ALB Style)

Yeh approach bilkul Ola/Uber jaisi hai. Tum bas destination bolo, routing system handle kar lega.

```yaml
# Kubernetes service configuration for Jio's 5G service discovery
apiVersion: v1
kind: Service
metadata:
  name: jio-5g-user-service
  annotations:
    # Load balancer configuration
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
    service.beta.kubernetes.io/aws-load-balancer-backend-protocol: "tcp"
    
    # Indian compliance and regional settings
    jio.compliance/telecom-regulatory: "dot-approved"
    jio.region/primary: "ap-south-1"
    jio.region/secondary: "ap-southeast-1"
    jio.latency/max-tolerable: "100ms"
    
    # Performance monitoring
    prometheus.io/scrape: "true"
    prometheus.io/port: "9090"
    prometheus.io/path: "/metrics"
spec:
  type: LoadBalancer
  sessionAffinity: ClientIP  # Important for user session continuity
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 3600  # 1 hour session stickiness
  selector:
    app: jio-5g-user-service
    version: stable
    compliance: dot-approved
  ports:
  - name: http
    port: 80
    targetPort: 8080
    protocol: TCP
  - name: grpc
    port: 443
    targetPort: 8443
    protocol: TCP

---
# Advanced ingress configuration with geographic routing
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: jio-user-service-ingress
  annotations:
    # Geographic routing for better performance
    nginx.ingress.kubernetes.io/configuration-snippet: |
      set $region "mumbai";
      if ($http_cf_ipcountry = "IN") {
        set $region "india";
      }
      if ($geoip_region = "MH") {
        set $region "mumbai";
      }
      if ($geoip_region = "DL") {
        set $region "delhi";
      }
      if ($geoip_region = "KA") {
        set $region "bangalore";
      }
      proxy_set_header X-User-Region $region;
    
    # Rate limiting for Indian traffic patterns
    nginx.ingress.kubernetes.io/rate-limit: "1000"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    nginx.ingress.kubernetes.io/rate-limit-connections: "100"
    
    # SSL and security
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.jio.com
    secretName: jio-api-tls
  rules:
  - host: api.jio.com
    http:
      paths:
      - path: /users
        pathType: Prefix
        backend:
          service:
            name: jio-5g-user-service
            port:
              number: 80
```

Aur iska advanced controller configuration:

```go
// Custom Kubernetes controller for Jio's service discovery
package main

import (
    "context"
    "fmt"
    "time"
    
    v1 "k8s.io/api/core/v1"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/rest"
)

type JioServiceDiscoveryController struct {
    clientset *kubernetes.Clientset
    namespace string
    regions   []string
}

func NewJioController() (*JioServiceDiscoveryController, error) {
    config, err := rest.InClusterConfig()
    if err != nil {
        return nil, err
    }
    
    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        return nil, err
    }
    
    return &JioServiceDiscoveryController{
        clientset: clientset,
        namespace: "jio-production",
        regions:   []string{"mumbai", "delhi", "bangalore", "hyderabad", "pune", "chennai"},
    }, nil
}

func (j *JioServiceDiscoveryController) DiscoverHealthyEndpoints(serviceName string, region string) ([]v1.Endpoints, error) {
    // Get service endpoints
    endpoints, err := j.clientset.CoreV1().Endpoints(j.namespace).Get(
        context.TODO(), serviceName, metav1.GetOptions{})
    if err != nil {
        return nil, err
    }
    
    var healthyEndpoints []v1.Endpoints
    
    for _, subset := range endpoints.Subsets {
        var healthyAddresses []v1.EndpointAddress
        
        for _, addr := range subset.Addresses {
            // Check if endpoint is in preferred region
            if podRegion, exists := addr.TargetRef.Labels["jio.region"]; exists {
                if podRegion == region || (region == "" && j.isRegionHealthy(podRegion)) {
                    // Perform health check
                    if j.isEndpointHealthy(addr.IP, subset.Ports[0].Port) {
                        healthyAddresses = append(healthyAddresses, addr)
                    }
                }
            }
        }
        
        if len(healthyAddresses) > 0 {
            healthySubset := v1.EndpointSubset{
                Addresses: healthyAddresses,
                Ports:     subset.Ports,
            }
            
            healthyEndpoint := v1.Endpoints{
                ObjectMeta: endpoints.ObjectMeta,
                Subsets:    []v1.EndpointSubset{healthySubset},
            }
            
            healthyEndpoints = append(healthyEndpoints, healthyEndpoint)
        }
    }
    
    return healthyEndpoints, nil
}

func (j *JioServiceDiscoveryController) isEndpointHealthy(ip string, port int32) bool {
    // Implement sophisticated health checking for Indian network conditions
    // Consider factors like:
    // - Network latency (important for 3G/4G users)
    // - Regional connectivity issues
    // - Peak traffic hours (6-9 PM)
    
    // Simplified implementation
    timeout := time.Duration(500) * time.Millisecond
    // Implementation would include actual HTTP/TCP health checks
    return true // Simplified for example
}

func (j *JioServiceDiscoveryController) isRegionHealthy(region string) bool {
    // Check regional health metrics
    // Consider factors like:
    // - Data center availability
    // - Network partition issues
    // - Regulatory compliance status
    
    healthyRegions := map[string]bool{
        "mumbai":    true,
        "delhi":     true,
        "bangalore": true,
        "hyderabad": true,
        "pune":      false, // Simulated outage
        "chennai":   true,
    }
    
    return healthyRegions[region]
}

// Advanced service mesh integration for Jio
func (j *JioServiceDiscoveryController) UpdateServiceMeshConfig(serviceName string) error {
    // Update Istio/Linkerd configuration based on discovered services
    // This would typically involve:
    // 1. Updating VirtualService configurations
    // 2. Modifying DestinationRule for load balancing
    // 3. Configuring traffic policies for Indian compliance
    
    return nil
}
```

**Server-Side Discovery ke Fayde**:
1. **Simple Clients**: Client sirf URL call karta hai, discovery logic handle nahi karta
2. **Centralized Updates**: Algorithm update sirf ek jagah karna hai
3. **Language Agnostic**: Koi bhi language use kar sakte ho
4. **Production Proven**: Kubernetes, AWS, GCP sabmein battle tested

**Nuksan**:
1. **Extra Network Hop**: Load balancer ke through jaana padta hai
2. **Single Point of Failure**: Load balancer down = entire system down
3. **Limited Customization**: Pre-built algorithms use karne padte hain

### Chapter 3: Registry-Based Discovery vs DNS-Based Discovery (35-50 Minutes)

#### Registry-Based Approach (Consul/Eureka)

Yeh approach bilkul Mumbai ke dabba-wallah union office jaisi hai. Central registration, real-time updates, detailed metadata.

```python
# Consul-based service discovery implementation for Swiggy
import consul
import json
import time
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class SwiggyServiceMetadata:
    """Service metadata specific to Swiggy's requirements"""
    service_name: str
    version: str
    region: str
    zone: str
    restaurant_partner: bool  # Can handle restaurant orders
    delivery_partner: bool    # Can handle delivery
    payment_partner: bool     # Can handle payments
    compliance_level: str     # FSSAI compliance level
    max_concurrent_orders: int
    avg_response_time_ms: int
    supported_cuisines: List[str]

class SwiggyServiceRegistry:
    """Production-grade service registry for Swiggy's microservices"""
    
    def __init__(self, consul_host='localhost', consul_port=8500):
        self.consul = consul.Consul(host=consul_host, port=consul_port)
        self.local_cache = {}
        self.cache_ttl = 30  # 30 seconds
        self.last_cache_update = {}
        
        # Start background health checking
        self.health_check_thread = threading.Thread(target=self._background_health_check)
        self.health_check_thread.daemon = True
        self.health_check_thread.start()
    
    def register_service(self, service_id: str, host: str, port: int, 
                        metadata: SwiggyServiceMetadata) -> bool:
        """Register a new service instance - like new delivery partner joining"""
        
        # Health check configuration for food delivery requirements
        health_check = {
            'http': f'http://{host}:{port}/health',
            'interval': '10s',    # Check every 10 seconds
            'timeout': '3s',      # 3 second timeout for Indian networks
            'deregister_critical_service_after': '30s'  # Auto-deregister if unhealthy
        }
        
        # Service registration with comprehensive metadata
        service_config = {
            'name': metadata.service_name,
            'id': service_id,
            'address': host,
            'port': port,
            'tags': [
                f'version:{metadata.version}',
                f'region:{metadata.region}',
                f'zone:{metadata.zone}',
                f'compliance:{metadata.compliance_level}'
            ],
            'meta': {
                'restaurant_partner': str(metadata.restaurant_partner).lower(),
                'delivery_partner': str(metadata.delivery_partner).lower(),
                'payment_partner': str(metadata.payment_partner).lower(),
                'max_concurrent_orders': str(metadata.max_concurrent_orders),
                'avg_response_time_ms': str(metadata.avg_response_time_ms),
                'supported_cuisines': ','.join(metadata.supported_cuisines),
                'registered_at': str(int(time.time())),
                'registration_source': 'swiggy_auto_discovery'
            },
            'check': health_check
        }
        
        try:
            result = self.consul.agent.service.register(**service_config)
            print(f"Service {service_id} registered successfully")
            return True
        except Exception as e:
            print(f"Failed to register service {service_id}: {e}")
            return False
    
    def discover_services(self, service_name: str, filters: Dict = None) -> List[Dict]:
        """Discover services with advanced filtering for Swiggy's use cases"""
        
        # Check cache first
        cache_key = f"{service_name}:{json.dumps(filters, sort_keys=True)}"
        if self._is_cache_valid(cache_key):
            return self.local_cache[cache_key]
        
        try:
            # Get all instances of the service
            _, services = self.consul.health.service(service_name, passing=True)
            
            valid_services = []
            for service in services:
                service_info = service['Service']
                node_info = service['Node']
                checks = service['Checks']
                
                # Basic service information
                instance = {
                    'id': service_info['ID'],
                    'name': service_info['Service'],
                    'address': service_info['Address'],
                    'port': service_info['Port'],
                    'tags': service_info['Tags'],
                    'meta': service_info['Meta'],
                    'node': node_info['Node'],
                    'datacenter': node_info['Datacenter'],
                    'health_status': 'passing' if all(check['Status'] == 'passing' for check in checks) else 'warning'
                }
                
                # Apply filters
                if self._matches_filters(instance, filters):
                    valid_services.append(instance)
            
            # Cache the results
            self.local_cache[cache_key] = valid_services
            self.last_cache_update[cache_key] = time.time()
            
            return valid_services
            
        except Exception as e:
            print(f"Service discovery failed for {service_name}: {e}")
            # Return cached results if available
            return self.local_cache.get(cache_key, [])
    
    def _matches_filters(self, instance: Dict, filters: Dict) -> bool:
        """Apply Swiggy-specific filters"""
        if not filters:
            return True
        
        meta = instance.get('meta', {})
        tags = instance.get('tags', [])
        
        # Region filter (very important for delivery optimization)
        if 'region' in filters:
            region_tag = f"region:{filters['region']}"
            if region_tag not in tags:
                return False
        
        # Capability filters
        if 'requires_restaurant_partner' in filters:
            if meta.get('restaurant_partner', 'false') != 'true':
                return False
        
        if 'requires_delivery_partner' in filters:
            if meta.get('delivery_partner', 'false') != 'true':
                return False
        
        if 'requires_payment_partner' in filters:
            if meta.get('payment_partner', 'false') != 'true':
                return False
        
        # Performance filters
        if 'max_response_time' in filters:
            avg_response = int(meta.get('avg_response_time_ms', '999999'))
            if avg_response > filters['max_response_time']:
                return False
        
        if 'min_capacity' in filters:
            max_orders = int(meta.get('max_concurrent_orders', '0'))
            if max_orders < filters['min_capacity']:
                return False
        
        # Cuisine filter
        if 'cuisine' in filters:
            supported_cuisines = meta.get('supported_cuisines', '').split(',')
            if filters['cuisine'] not in supported_cuisines:
                return False
        
        return True
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.local_cache:
            return False
        
        last_update = self.last_cache_update.get(cache_key, 0)
        return (time.time() - last_update) < self.cache_ttl
    
    def _background_health_check(self):
        """Background thread for additional health monitoring"""
        while True:
            try:
                # Check critical services
                critical_services = ['order-processor', 'payment-gateway', 'delivery-assignment']
                
                for service_name in critical_services:
                    services = self.discover_services(service_name)
                    healthy_count = len([s for s in services if s['health_status'] == 'passing'])
                    
                    if healthy_count == 0:
                        print(f"CRITICAL: No healthy instances of {service_name}")
                        # Trigger alert to Swiggy's ops team
                        self._trigger_ops_alert(service_name, "NO_HEALTHY_INSTANCES")
                    elif healthy_count < 2:
                        print(f"WARNING: Only {healthy_count} healthy instance(s) of {service_name}")
                        self._trigger_ops_alert(service_name, "LOW_INSTANCE_COUNT")
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Background health check error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _trigger_ops_alert(self, service_name: str, alert_type: str):
        """Trigger alert to operations team"""
        # Implementation would integrate with Swiggy's alerting system
        print(f"ALERT: {alert_type} for service {service_name}")

# Usage example for Swiggy's order processing
def swiggy_order_processing_example():
    """Real-world example of service discovery in Swiggy's order flow"""
    
    registry = SwiggyServiceRegistry()
    
    # Register a new order processor service
    order_processor_metadata = SwiggyServiceMetadata(
        service_name="order-processor",
        version="2.1.3",
        region="mumbai",
        zone="andheri-east",
        restaurant_partner=True,
        delivery_partner=False,
        payment_partner=True,
        compliance_level="fssai_licensed",
        max_concurrent_orders=500,
        avg_response_time_ms=150,
        supported_cuisines=["north_indian", "south_indian", "chinese", "continental"]
    )
    
    registry.register_service(
        service_id="order-processor-andheri-01",
        host="10.0.1.15",
        port=8080,
        metadata=order_processor_metadata
    )
    
    # Discover delivery assignment service for specific zone
    delivery_services = registry.discover_services(
        service_name="delivery-assignment",
        filters={
            'region': 'mumbai',
            'requires_delivery_partner': True,
            'max_response_time': 200,
            'min_capacity': 100
        }
    )
    
    print(f"Found {len(delivery_services)} delivery assignment services")
    for service in delivery_services:
        print(f"  - {service['id']} at {service['address']}:{service['port']}")
        print(f"    Capacity: {service['meta']['max_concurrent_orders']}")
        print(f"    Response time: {service['meta']['avg_response_time_ms']}ms")
```

**Registry-Based ke Fayde**:
1. **Rich Metadata**: Service ke baare mein detailed information store kar sakte ho
2. **Real-time Updates**: Instant service registration/deregistration
3. **Health Checking**: Built-in health monitoring
4. **Query Flexibility**: Complex queries kar sakte ho
5. **Service Dependencies**: Service relationships track kar sakte ho

**Nuksan**:
1. **Additional Infrastructure**: Registry service maintain karna padta hai
2. **Network Dependency**: Registry down = discovery down
3. **Consistency Challenges**: Multiple regions mein sync issues
4. **Complex Setup**: Initial setup and maintenance overhead

#### DNS-Based Approach

Yeh approach sabse simple hai - bilkul telephone directory jaisi. Service name = DNS name.

```python
# DNS-based service discovery for simple microservices
import socket
import dns.resolver
import random
import time
from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class DNSServiceEndpoint:
    """DNS-resolved service endpoint"""
    host: str
    port: int
    priority: int = 0
    weight: int = 1
    ttl: int = 300

class DNSServiceDiscovery:
    """DNS-based service discovery with Indian ISP optimizations"""
    
    def __init__(self, domain_suffix: str = "internal.mycompany.com"):
        self.domain_suffix = domain_suffix
        self.dns_cache = {}
        self.cache_ttl = 60  # 60 seconds for Indian network conditions
        self.dns_servers = [
            '8.8.8.8',      # Google DNS
            '1.1.1.1',      # Cloudflare DNS  
            '208.67.222.222'  # OpenDNS
        ]
        
    def discover_service(self, service_name: str) -> List[DNSServiceEndpoint]:
        """Discover service using DNS SRV records"""
        
        # Check cache first
        cache_key = f"_srv_{service_name}"
        if self._is_cache_valid(cache_key):
            return self.dns_cache[cache_key]
        
        srv_name = f"_{service_name}._tcp.{self.domain_suffix}"
        endpoints = []
        
        try:
            # Try SRV record lookup first (preferred method)
            answers = dns.resolver.resolve(srv_name, 'SRV')
            
            for rdata in answers:
                endpoint = DNSServiceEndpoint(
                    host=str(rdata.target).rstrip('.'),
                    port=rdata.port,
                    priority=rdata.priority,
                    weight=rdata.weight,
                    ttl=answers.ttl
                )
                endpoints.append(endpoint)
                
        except dns.resolver.NXDOMAIN:
            # Fallback to A record lookup
            try:
                a_name = f"{service_name}.{self.domain_suffix}"
                answers = dns.resolver.resolve(a_name, 'A')
                
                # Assume standard ports for different services
                service_ports = {
                    'api': 8080,
                    'web': 80,
                    'database': 5432,
                    'cache': 6379,
                    'messaging': 5672
                }
                
                port = service_ports.get(service_name.split('-')[0], 8080)
                
                for rdata in answers:
                    endpoint = DNSServiceEndpoint(
                        host=str(rdata),
                        port=port,
                        ttl=answers.ttl
                    )
                    endpoints.append(endpoint)
                    
            except Exception as e:
                print(f"DNS lookup failed for {service_name}: {e}")
                
        except Exception as e:
            print(f"SRV lookup failed for {service_name}: {e}")
        
        # Cache the results
        if endpoints:
            self.dns_cache[cache_key] = endpoints
            self.dns_cache[f"{cache_key}_timestamp"] = time.time()
        
        return endpoints
    
    def select_endpoint(self, endpoints: List[DNSServiceEndpoint]) -> Optional[DNSServiceEndpoint]:
        """Select best endpoint using weighted random selection"""
        if not endpoints:
            return None
        
        # Sort by priority first
        endpoints.sort(key=lambda x: x.priority)
        
        # Get endpoints with lowest priority
        min_priority = endpoints[0].priority
        priority_endpoints = [ep for ep in endpoints if ep.priority == min_priority]
        
        # Weighted selection among same priority endpoints
        if len(priority_endpoints) == 1:
            return priority_endpoints[0]
        
        total_weight = sum(ep.weight for ep in priority_endpoints)
        if total_weight == 0:
            return random.choice(priority_endpoints)
        
        r = random.randint(1, total_weight)
        current_weight = 0
        
        for endpoint in priority_endpoints:
            current_weight += endpoint.weight
            if current_weight >= r:
                return endpoint
        
        return priority_endpoints[-1]
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if DNS cache is still valid"""
        if cache_key not in self.dns_cache:
            return False
        
        timestamp_key = f"{cache_key}_timestamp"
        if timestamp_key not in self.dns_cache:
            return False
        
        age = time.time() - self.dns_cache[timestamp_key]
        return age < self.cache_ttl

# Example DNS configuration for Indian company
dns_config_example = """
# DNS Zone configuration for mycompany.internal

; SRV Records for microservices
_payment._tcp.mycompany.internal.    300 IN SRV 10 60 8080 payment1.mumbai.mycompany.internal.
_payment._tcp.mycompany.internal.    300 IN SRV 10 40 8080 payment2.mumbai.mycompany.internal.
_payment._tcp.mycompany.internal.    300 IN SRV 20 100 8080 payment1.delhi.mycompany.internal.

_user._tcp.mycompany.internal.       300 IN SRV 10 50 8080 user1.mumbai.mycompany.internal.
_user._tcp.mycompany.internal.       300 IN SRV 10 50 8080 user2.mumbai.mycompany.internal.
_user._tcp.mycompany.internal.       300 IN SRV 20 100 8080 user1.bangalore.mycompany.internal.

; A Records for direct access
payment1.mumbai.mycompany.internal.  300 IN A 10.0.1.10
payment2.mumbai.mycompany.internal.  300 IN A 10.0.1.11
payment1.delhi.mycompany.internal.   300 IN A 10.1.1.10

user1.mumbai.mycompany.internal.     300 IN A 10.0.2.10
user2.mumbai.mycompany.internal.     300 IN A 10.0.2.11
user1.bangalore.mycompany.internal.  300 IN A 10.2.1.10

; CNAME for load balancing
api.mycompany.internal.              300 IN CNAME api-lb.mumbai.mycompany.internal.
web.mycompany.internal.              300 IN CNAME web-lb.mumbai.mycompany.internal.
"""

# Usage example
def indian_startup_dns_example():
    """Example usage for Indian startup with multi-region setup"""
    
    discovery = DNSServiceDiscovery("internal.mystartup.in")
    
    # Discover payment service
    payment_endpoints = discovery.discover_service("payment")
    
    if payment_endpoints:
        selected = discovery.select_endpoint(payment_endpoints)
        print(f"Selected payment endpoint: {selected.host}:{selected.port}")
        print(f"Priority: {selected.priority}, Weight: {selected.weight}")
        
        # Test connectivity
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)  # 3 second timeout for Indian networks
            result = sock.connect_ex((selected.host, selected.port))
            sock.close()
            
            if result == 0:
                print("✅ Service is reachable")
            else:
                print("❌ Service is not reachable")
                
        except Exception as e:
            print(f"Connection test failed: {e}")
    else:
        print("No payment service endpoints found")
```

**DNS-Based ke Fayde**:
1. **Universal Support**: Har language/platform DNS support karta hai
2. **Zero Infrastructure**: Additional services install nahi karne padte
3. **Caching**: Built-in DNS caching for performance
4. **Simple**: Configuration bhi simple, usage bhi simple

**Nuksan**:
1. **Limited Metadata**: Sirf IP aur port, koi additional info nahi
2. **No Health Checking**: DNS automatically unhealthy services remove nahi karta
3. **TTL Issues**: Changes propagate hone mein time lagta hai
4. **No Load Balancing Logic**: Basic weight-based selection hi available hai

### Chapter 4: Health Checking aur Load Balancing (50-60 Minutes)

#### Advanced Health Checking Strategies

Mumbai ke dabba-wallah system mein dekho - har delivery route continuously monitor hota hai. Same concept microservices mein!

```python
# Comprehensive health checking system for Indian microservices
import asyncio
import aiohttp
import time
import statistics
import threading
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class HealthCheckResult:
    """Health check result with Indian network considerations"""
    service_id: str
    endpoint: str
    status: HealthStatus
    response_time_ms: int
    error_message: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    network_type: str = "4G"  # 3G, 4G, 5G, WiFi, Fiber
    region: str = "unknown"
    
class IndianNetworkAwareHealthChecker:
    """Health checker optimized for Indian network conditions"""
    
    def __init__(self):
        self.health_history = defaultdict(lambda: deque(maxlen=50))
        self.circuit_breakers = {}
        self.region_thresholds = {
            # Latency thresholds based on Indian infrastructure
            "mumbai": {"3G": 800, "4G": 400, "5G": 100, "fiber": 50},
            "delhi": {"3G": 900, "4G": 450, "5G": 120, "fiber": 60},
            "bangalore": {"3G": 700, "4G": 350, "5G": 90, "fiber": 40},
            "hyderabad": {"3G": 750, "4G": 380, "5G": 100, "fiber": 45},
            "rural": {"3G": 1500, "4G": 800, "5G": 300, "fiber": 150}
        }
        
    async def check_http_health(self, service_id: str, endpoint: str, 
                               region: str = "mumbai", network_type: str = "4G") -> HealthCheckResult:
        """HTTP health check with regional optimization"""
        
        start_time = time.time()
        
        # Get appropriate timeout based on region and network
        timeout = self._get_timeout_for_region_network(region, network_type)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{endpoint}/health",
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    
                    response_time_ms = int((time.time() - start_time) * 1000)
                    
                    if response.status == 200:
                        # Check response content for detailed health
                        try:
                            health_data = await response.json()
                            detailed_status = self._evaluate_detailed_health(
                                health_data, response_time_ms, region, network_type
                            )
                        except:
                            # Fallback to simple status check
                            detailed_status = HealthStatus.HEALTHY if response_time_ms < timeout * 1000 else HealthStatus.DEGRADED
                            
                        result = HealthCheckResult(
                            service_id=service_id,
                            endpoint=endpoint,
                            status=detailed_status,
                            response_time_ms=response_time_ms,
                            network_type=network_type,
                            region=region
                        )
                    else:
                        result = HealthCheckResult(
                            service_id=service_id,
                            endpoint=endpoint,
                            status=HealthStatus.UNHEALTHY,
                            response_time_ms=response_time_ms,
                            error_message=f"HTTP {response.status}",
                            network_type=network_type,
                            region=region
                        )
                        
        except asyncio.TimeoutError:
            result = HealthCheckResult(
                service_id=service_id,
                endpoint=endpoint,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=timeout * 1000,
                error_message="Timeout",
                network_type=network_type,
                region=region
            )
            
        except Exception as e:
            result = HealthCheckResult(
                service_id=service_id,
                endpoint=endpoint,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=int((time.time() - start_time) * 1000),
                error_message=str(e),
                network_type=network_type,
                region=region
            )
        
        # Store result in history
        self.health_history[service_id].append(result)
        
        return result
    
    def _get_timeout_for_region_network(self, region: str, network_type: str) -> float:
        """Get appropriate timeout based on region and network type"""
        thresholds = self.region_thresholds.get(region, self.region_thresholds["rural"])
        base_threshold = thresholds.get(network_type, thresholds["3G"])
        
        # Convert to seconds and add buffer
        return (base_threshold / 1000) * 1.5  # 1.5x buffer for health checks
    
    def _evaluate_detailed_health(self, health_data: Dict, response_time_ms: int, 
                                region: str, network_type: str) -> HealthStatus:
        """Evaluate health based on detailed response data"""
        
        # Check various health indicators
        cpu_usage = health_data.get('cpu_usage_percent', 0)
        memory_usage = health_data.get('memory_usage_percent', 0)
        disk_usage = health_data.get('disk_usage_percent', 0)
        active_connections = health_data.get('active_connections', 0)
        error_rate = health_data.get('error_rate_percent', 0)
        
        # Regional threshold for latency
        latency_threshold = self.region_thresholds.get(region, self.region_thresholds["rural"])[network_type]
        
        # Health scoring
        health_score = 100
        
        # Penalize high resource usage
        if cpu_usage > 80:
            health_score -= 20
        elif cpu_usage > 60:
            health_score -= 10
            
        if memory_usage > 85:
            health_score -= 25
        elif memory_usage > 70:
            health_score -= 15
            
        if disk_usage > 90:
            health_score -= 30
        elif disk_usage > 80:
            health_score -= 15
            
        # Penalize high latency
        if response_time_ms > latency_threshold:
            health_score -= 25
        elif response_time_ms > latency_threshold * 0.8:
            health_score -= 10
            
        # Penalize error rates
        if error_rate > 5:
            health_score -= 30
        elif error_rate > 2:
            health_score -= 15
            
        # Determine status based on score
        if health_score >= 80:
            return HealthStatus.HEALTHY
        elif health_score >= 50:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.UNHEALTHY
    
    def get_service_health_trend(self, service_id: str, window_minutes: int = 10) -> Dict:
        """Get health trend for service over time window"""
        
        if service_id not in self.health_history:
            return {"status": "unknown", "trend": "unknown"}
        
        now = time.time()
        cutoff_time = now - (window_minutes * 60)
        
        recent_results = [
            result for result in self.health_history[service_id]
            if result.timestamp >= cutoff_time
        ]
        
        if not recent_results:
            return {"status": "unknown", "trend": "unknown"}
        
        # Calculate statistics
        total_checks = len(recent_results)
        healthy_checks = len([r for r in recent_results if r.status == HealthStatus.HEALTHY])
        degraded_checks = len([r for r in recent_results if r.status == HealthStatus.DEGRADED])
        unhealthy_checks = len([r for r in recent_results if r.status == HealthStatus.UNHEALTHY])
        
        avg_response_time = statistics.mean([r.response_time_ms for r in recent_results])
        
        # Determine overall status
        healthy_percentage = (healthy_checks / total_checks) * 100
        
        if healthy_percentage >= 80:
            overall_status = HealthStatus.HEALTHY
        elif healthy_percentage >= 50:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.UNHEALTHY
        
        # Determine trend (compare first half vs second half)
        mid_point = len(recent_results) // 2
        if mid_point > 0:
            first_half_healthy = len([r for r in recent_results[:mid_point] if r.status == HealthStatus.HEALTHY])
            second_half_healthy = len([r for r in recent_results[mid_point:] if r.status == HealthStatus.HEALTHY])
            
            first_half_percentage = (first_half_healthy / mid_point) * 100 if mid_point > 0 else 0
            second_half_percentage = (second_half_healthy / (len(recent_results) - mid_point)) * 100
            
            if second_half_percentage > first_half_percentage + 10:
                trend = "improving"
            elif second_half_percentage < first_half_percentage - 10:
                trend = "degrading"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "status": overall_status.value,
            "trend": trend,
            "total_checks": total_checks,
            "healthy_percentage": healthy_percentage,
            "avg_response_time_ms": int(avg_response_time),
            "error_count": unhealthy_checks
        }

# Usage example for Jio's 5G service health monitoring
async def jio_5g_health_monitoring_example():
    """Health monitoring for Jio's 5G network services"""
    
    health_checker = IndianNetworkAwareHealthChecker()
    
    # Define Jio's critical services across regions
    jio_services = [
        {"id": "auth-service-mumbai", "endpoint": "http://10.0.1.10:8080", "region": "mumbai"},
        {"id": "auth-service-delhi", "endpoint": "http://10.1.1.10:8080", "region": "delhi"},
        {"id": "billing-service-bangalore", "endpoint": "http://10.2.1.10:8080", "region": "bangalore"},
        {"id": "network-service-hyderabad", "endpoint": "http://10.3.1.10:8080", "region": "hyderabad"}
    ]
    
    # Continuous health monitoring
    while True:
        health_results = []
        
        for service in jio_services:
            # Check health with 5G network assumptions
            result = await health_checker.check_http_health(
                service_id=service["id"],
                endpoint=service["endpoint"],
                region=service["region"],
                network_type="5G"
            )
            health_results.append(result)
            
            # Get health trend
            trend = health_checker.get_service_health_trend(service["id"])
            
            print(f"Service: {service['id']}")
            print(f"  Status: {result.status.value}")
            print(f"  Response Time: {result.response_time_ms}ms")
            print(f"  Trend: {trend['trend']} ({trend['healthy_percentage']:.1f}% healthy)")
            
            # Alert if service is degrading
            if trend['trend'] == 'degrading' or result.status == HealthStatus.UNHEALTHY:
                print(f"  🚨 ALERT: Service {service['id']} needs attention!")
        
        # Wait before next check cycle
        await asyncio.sleep(30)

# Run the example
if __name__ == "__main__":
    asyncio.run(jio_5g_health_monitoring_example())
```

Yeh comprehensive health checking system hai jo Indian network conditions ko consider karta hai. Peak traffic hours, network quality, regional differences - sab kuch!

---

**Part 1 Summary (60 Minutes Complete)**

Doston, yeh tha Part 1 - Service Discovery ke foundations! Humne seekha:

1. **Mumbai Tiffin System Analogy**: Kaise ek perfect coordination system inspire kar sakta hai microservices architecture
2. **Client-Side vs Server-Side Discovery**: Dono approaches ke pros and cons
3. **Registry vs DNS**: Kab kya use karna chahiye
4. **Health Checking**: Indian network conditions ke liye optimized monitoring

**Next up in Part 2**: Production implementation patterns, Kubernetes service mesh integration, aur real case studies from PhonePe, Paytm, aur Jio!

Stay tuned! 🚀

---

*Word Count: Part 1 = 7,247 words*
*Total Progress: 7,247 / 20,000+ words*
*Time: 0-60 minutes covered*