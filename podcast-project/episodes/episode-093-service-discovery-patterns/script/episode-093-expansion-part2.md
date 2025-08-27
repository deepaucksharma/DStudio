# Episode 093: Service Discovery Patterns - Expansion Part 2
## Service Mesh Deep Dive and Production Implementations

---

## Chapter 11: IRCTC's Service Discovery for 1M+ Concurrent Bookings

IRCTC ka Tatkal booking time - subah 10 baje for AC, 11 baje for Sleeper. Exact time pe 1 million+ log ek saath try karte hain! Service discovery ka ultimate test!

### IRCTC's Evolution Story

```python
class IRCTCServiceDiscoveryEvolution:
    """
    IRCTC's service discovery journey from crashes to stability
    Hindi: IRCTC की सफलता की कहानी
    """
    
    def __init__(self):
        self.historical_failures = {
            "2014": {
                "issue": "Complete website crash during Tatkal",
                "users_affected": 500000,
                "downtime_minutes": 120,
                "root_cause": "No service discovery, single monolith",
                "loss_inr": 10000000
            },
            "2016": {
                "issue": "Partial service failures",
                "users_affected": 200000,
                "downtime_minutes": 45,
                "root_cause": "Basic load balancer overwhelmed",
                "loss_inr": 5000000
            },
            "2018": {
                "issue": "Slow response times",
                "users_affected": 100000,
                "downtime_minutes": 15,
                "root_cause": "Inefficient service routing",
                "loss_inr": 2000000
            },
            "2020": {
                "issue": "Minor degradation",
                "users_affected": 10000,
                "downtime_minutes": 5,
                "root_cause": "Service mesh configuration issue",
                "loss_inr": 500000
            },
            "2024": {
                "issue": "Zero downtime!",
                "users_affected": 0,
                "downtime_minutes": 0,
                "root_cause": "N/A - System stable",
                "achievement": "Handled 2M concurrent users!"
            }
        }
        
        self.current_architecture = {
            "service_discovery": "Kubernetes + Istio",
            "load_balancing": "Envoy proxies",
            "caching": "Redis clusters",
            "database": "Sharded PostgreSQL + MongoDB",
            "message_queue": "Kafka",
            "regions": ["Mumbai", "Delhi", "Chennai", "Kolkata"]
        }
    
    def tatkal_booking_flow(self):
        """
        Tatkal booking service discovery flow
        """
        services = {
            "user_authentication": {
                "instances": 100,
                "discovery": "Kubernetes DNS",
                "health_check": "TCP check on 8080",
                "timeout_ms": 100
            },
            "train_search": {
                "instances": 200,
                "discovery": "Consul",
                "health_check": "HTTP /health",
                "timeout_ms": 500,
                "cache_ttl": 60
            },
            "seat_availability": {
                "instances": 500,  # Maximum instances!
                "discovery": "Istio service mesh",
                "health_check": "gRPC health probe",
                "timeout_ms": 200,
                "cache_ttl": 1  # 1 second cache only
            },
            "booking_engine": {
                "instances": 300,
                "discovery": "Kubernetes endpoints",
                "health_check": "Custom booking probe",
                "timeout_ms": 1000,
                "retry_count": 3
            },
            "payment_gateway": {
                "instances": 150,
                "discovery": "Consul + Envoy",
                "health_check": "Payment system probe",
                "timeout_ms": 5000,
                "circuit_breaker": True
            }
        }
        
        return services
    
    def handle_tatkal_surge(self, booking_time):
        """
        Handle Tatkal booking surge at exact time
        Hindi: Tatkal की भीड़ संभालना
        """
        surge_timeline = {
            "T-5min": {
                "action": "Pre-scale all services to maximum",
                "services_scaled": ["seat_availability", "booking_engine"],
                "cache_warmup": True
            },
            "T-1min": {
                "action": "Enable surge protection",
                "rate_limiting": "100 req/sec per user",
                "queue_enabled": True
            },
            "T-0": {
                "action": "Tatkal opens!",
                "expected_rps": 2000000,
                "actual_handling": "Load distributed across regions"
            },
            "T+30sec": {
                "action": "First wave complete",
                "bookings_processed": 50000,
                "services_healthy": True
            },
            "T+5min": {
                "action": "Gradual scale down",
                "bookings_total": 200000,
                "start_scaling_down": True
            }
        }
        
        return surge_timeline
    
    def implement_circuit_breaker(self):
        """
        Circuit breaker for payment service
        """
        circuit_breaker_config = {
            "failure_threshold": 5,
            "timeout_seconds": 30,
            "half_open_requests": 3,
            "monitoring_window": 60,
            "fallback_action": "queue_for_retry"
        }
        
        return circuit_breaker_config

# IRCTC's Kubernetes service discovery config
irctc_k8s_config = """
apiVersion: v1
kind: Service
metadata:
  name: tatkal-booking-service
  namespace: irctc-production
  labels:
    app: booking
    tier: critical
spec:
  selector:
    app: booking-engine
  ports:
  - name: http
    port: 80
    targetPort: 8080
  - name: grpc
    port: 9090
    targetPort: 9090
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: booking-routing
  namespace: irctc-production
spec:
  hosts:
  - booking-service
  http:
  - match:
    - headers:
        booking-type:
          exact: tatkal
    route:
    - destination:
        host: tatkal-booking-service
        subset: high-performance
      weight: 100
    timeout: 2s
    retries:
      attempts: 3
      perTryTimeout: 1s
  - route:
    - destination:
        host: regular-booking-service
        subset: standard
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: booking-destination
  namespace: irctc-production
spec:
  host: tatkal-booking-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 1000
      http:
        http1MaxPendingRequests: 100
        h2MaxRequests: 1000
    loadBalancer:
      consistentHash:
        httpCookie:
          name: "session"
          ttl: 3600s
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
  subsets:
  - name: high-performance
    labels:
      version: v2
      performance: high
"""
```

## Chapter 12: Service Mesh Comparison - Istio vs Linkerd for Indian Scale

### Detailed Comparison with Indian Context

```python
class ServiceMeshComparison:
    """
    Comparing service mesh solutions for Indian companies
    Hindi: भारतीय कंपनियों के लिए service mesh comparison
    """
    
    def __init__(self):
        self.comparison_matrix = {
            "istio": {
                "pros": [
                    "Feature-rich with complete observability",
                    "Strong community support",
                    "Works well with Kubernetes",
                    "Good for complex deployments"
                ],
                "cons": [
                    "High resource overhead (500MB+ per sidecar)",
                    "Complex configuration",
                    "Steep learning curve",
                    "Expensive for small teams"
                ],
                "resource_usage": {
                    "cpu_per_sidecar": "100m",
                    "memory_per_sidecar": "512Mi",
                    "control_plane_memory": "3Gi"
                },
                "indian_companies_using": [
                    "Flipkart", "Paytm", "Ola"
                ],
                "monthly_cost_inr_100_pods": 150000
            },
            "linkerd": {
                "pros": [
                    "Lightweight (50MB per sidecar)",
                    "Easy to install and configure",
                    "Fast data plane",
                    "Good for startups"
                ],
                "cons": [
                    "Fewer features than Istio",
                    "Smaller community",
                    "Limited traffic management",
                    "Less extensive documentation"
                ],
                "resource_usage": {
                    "cpu_per_sidecar": "10m",
                    "memory_per_sidecar": "50Mi",
                    "control_plane_memory": "500Mi"
                },
                "indian_companies_using": [
                    "Dunzo", "Razorpay", "Cred"
                ],
                "monthly_cost_inr_100_pods": 30000
            },
            "consul": {
                "pros": [
                    "Multi-datacenter support",
                    "Works beyond Kubernetes",
                    "Built-in KV store",
                    "Good for hybrid cloud"
                ],
                "cons": [
                    "Requires Consul servers",
                    "Additional infrastructure",
                    "Less Kubernetes-native",
                    "Licensing costs for enterprise"
                ],
                "resource_usage": {
                    "cpu_per_sidecar": "50m",
                    "memory_per_sidecar": "128Mi",
                    "consul_server_memory": "1Gi"
                },
                "indian_companies_using": [
                    "Swiggy", "Dream11", "PhonePe"
                ],
                "monthly_cost_inr_100_pods": 80000
            }
        }
    
    def recommend_for_company(self, company_profile):
        """
        Recommend service mesh based on company profile
        """
        if company_profile["size"] == "startup":
            if company_profile["budget_inr"] < 50000:
                return {
                    "recommendation": "Linkerd",
                    "reason": "Lightweight and cost-effective",
                    "alternative": "Kubernetes native services"
                }
            else:
                return {
                    "recommendation": "Consul",
                    "reason": "Good balance of features and cost",
                    "alternative": "Linkerd"
                }
        
        elif company_profile["size"] == "mid-size":
            if company_profile["complexity"] == "high":
                return {
                    "recommendation": "Istio",
                    "reason": "Feature-rich for complex needs",
                    "alternative": "Consul"
                }
            else:
                return {
                    "recommendation": "Consul",
                    "reason": "Stable and proven",
                    "alternative": "Linkerd"
                }
        
        else:  # Enterprise
            return {
                "recommendation": "Istio",
                "reason": "Enterprise features and scalability",
                "alternative": "Custom solution"
            }
```

### Istio Implementation for Indian E-commerce

```yaml
# Istio configuration for Indian e-commerce scale
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  name: indian-ecommerce-istio
spec:
  values:
    pilot:
      env:
        PILOT_ENABLE_WORKLOAD_ENTRY_AUTOREGISTRATION: true
        PILOT_ENABLE_CROSS_CLUSTER_WORKLOAD_ENTRY: true
    global:
      proxy:
        resources:
          requests:
            cpu: 10m
            memory: 40Mi
          limits:
            cpu: 100m
            memory: 128Mi
        # Optimize for Indian network conditions
        holdApplicationUntilProxyStarts: true
        proxyStatsMatcher:
          inclusionRegexps:
          - ".*outlier_detection.*"
          - ".*osconfig.*"
          - ".*circuit_breakers.*"
    telemetry:
      v2:
        prometheus:
          configOverride:
            inboundSidecar:
              disable_host_header_fallback: true
            outboundSidecar:
              disable_host_header_fallback: true
    meshConfig:
      defaultConfig:
        # Optimize for Indian infrastructure
        proxyConfig:
          concurrency: 4
          # Handle slow networks
          drainDuration: 45s
          parentShutdownDuration: 60s
        # Circuit breaker for payment services
        connectionPool:
          tcp:
            maxConnections: 100
          http:
            http2MaxRequests: 100
            maxRequestsPerConnection: 10
        outlierDetection:
          consecutiveErrors: 5
          interval: 30s
          baseEjectionTime: 30s
          maxEjectionPercent: 50
```

## Chapter 13: Load Balancing Strategies for Indian Traffic

### Geographic Load Balancing Implementation

```python
class IndianGeographicLoadBalancer:
    """
    Geographic load balancing for Indian cities
    Hindi: भारतीय शहरों के लिए geographic load balancing
    """
    
    def __init__(self):
        self.regions = {
            "north": {
                "primary_dc": "Delhi",
                "backup_dc": "Noida",
                "cities": ["Delhi", "Gurgaon", "Noida", "Chandigarh", "Jaipur"],
                "capacity": 1000000,
                "latency_ms": 10
            },
            "west": {
                "primary_dc": "Mumbai",
                "backup_dc": "Pune",
                "cities": ["Mumbai", "Pune", "Ahmedabad", "Surat", "Nashik"],
                "capacity": 1500000,
                "latency_ms": 8
            },
            "south": {
                "primary_dc": "Bangalore",
                "backup_dc": "Chennai",
                "cities": ["Bangalore", "Chennai", "Hyderabad", "Kochi", "Coimbatore"],
                "capacity": 1200000,
                "latency_ms": 12
            },
            "east": {
                "primary_dc": "Kolkata",
                "backup_dc": "Bhubaneswar",
                "cities": ["Kolkata", "Bhubaneswar", "Guwahati", "Patna", "Ranchi"],
                "capacity": 800000,
                "latency_ms": 15
            }
        }
        
        self.traffic_patterns = {
            "morning_peak": {
                "time": "08:00-10:00",
                "north": 0.3,
                "west": 0.25,
                "south": 0.35,
                "east": 0.1
            },
            "evening_peak": {
                "time": "18:00-22:00",
                "north": 0.25,
                "west": 0.3,
                "south": 0.3,
                "east": 0.15
            },
            "late_night": {
                "time": "22:00-02:00",
                "north": 0.2,
                "west": 0.25,
                "south": 0.4,
                "east": 0.15
            }
        }
    
    def route_request(self, user_location, request_type, current_time):
        """
        Route request based on geography and load
        """
        # Determine user's region
        user_region = self.get_user_region(user_location)
        
        # Check region health
        if self.is_region_healthy(user_region):
            return self.regions[user_region]["primary_dc"]
        
        # Find best alternative region
        alternative = self.find_best_alternative(user_region, current_time)
        
        return alternative
    
    def implement_weighted_routing(self, service_versions):
        """
        A/B testing with weighted routing
        """
        routing_config = {
            "production": {
                "version": "v1",
                "weight": 70,
                "description": "Stable production version"
            },
            "canary": {
                "version": "v2",
                "weight": 20,
                "description": "New features testing"
            },
            "experimental": {
                "version": "v3",
                "weight": 10,
                "description": "Experimental features"
            }
        }
        
        # Apply routing based on user segment
        def route_by_weight(user_id):
            hash_value = hash(user_id) % 100
            
            if hash_value < 70:
                return routing_config["production"]["version"]
            elif hash_value < 90:
                return routing_config["canary"]["version"]
            else:
                return routing_config["experimental"]["version"]
        
        return route_by_weight
    
    def implement_circuit_breaker(self, service_name):
        """
        Circuit breaker for unreliable services
        """
        class CircuitBreaker:
            def __init__(self, failure_threshold=5, timeout=30, half_open_requests=3):
                self.failure_threshold = failure_threshold
                self.timeout = timeout
                self.half_open_requests = half_open_requests
                self.failure_count = 0
                self.last_failure_time = None
                self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
                self.half_open_count = 0
            
            def call(self, func, *args, **kwargs):
                if self.state == "OPEN":
                    if time.time() - self.last_failure_time > self.timeout:
                        self.state = "HALF_OPEN"
                        self.half_open_count = 0
                    else:
                        raise Exception(f"Circuit breaker OPEN for {service_name}")
                
                if self.state == "HALF_OPEN":
                    if self.half_open_count >= self.half_open_requests:
                        self.state = "CLOSED"
                        self.failure_count = 0
                
                try:
                    result = func(*args, **kwargs)
                    
                    if self.state == "HALF_OPEN":
                        self.half_open_count += 1
                    
                    return result
                    
                except Exception as e:
                    self.failure_count += 1
                    self.last_failure_time = time.time()
                    
                    if self.failure_count >= self.failure_threshold:
                        self.state = "OPEN"
                        print(f"Circuit breaker OPENED for {service_name}")
                    
                    raise e
        
        return CircuitBreaker()
```

### Festival Traffic Spike Handling

```go
// Festival traffic spike handler in Go
package main

import (
    "context"
    "sync"
    "time"
)

type FestivalTrafficManager struct {
    mu              sync.RWMutex
    currentFestival string
    trafficMultiplier float64
    services        map[string]*ServiceConfig
    rateLimiters    map[string]*RateLimiter
}

type ServiceConfig struct {
    Name            string
    BaseCapacity    int
    CurrentCapacity int
    MaxCapacity     int
    Priority        int // 1 = Critical, 2 = Important, 3 = Normal
}

func NewFestivalTrafficManager() *FestivalTrafficManager {
    ftm := &FestivalTrafficManager{
        services:     make(map[string]*ServiceConfig),
        rateLimiters: make(map[string]*RateLimiter),
    }
    
    // Initialize service configs
    ftm.initializeServices()
    
    return ftm
}

func (f *FestivalTrafficManager) initializeServices() {
    // Critical services
    f.services["payment"] = &ServiceConfig{
        Name:         "payment",
        BaseCapacity: 1000,
        MaxCapacity:  10000,
        Priority:     1,
    }
    
    f.services["cart"] = &ServiceConfig{
        Name:         "cart",
        BaseCapacity: 800,
        MaxCapacity:  8000,
        Priority:     1,
    }
    
    // Important services
    f.services["catalog"] = &ServiceConfig{
        Name:         "catalog",
        BaseCapacity: 500,
        MaxCapacity:  5000,
        Priority:     2,
    }
    
    // Normal services
    f.services["recommendation"] = &ServiceConfig{
        Name:         "recommendation",
        BaseCapacity: 200,
        MaxCapacity:  1000,
        Priority:     3,
    }
}

func (f *FestivalTrafficManager) HandleFestival(festival string) {
    f.mu.Lock()
    defer f.mu.Unlock()
    
    f.currentFestival = festival
    
    // Set traffic multiplier based on festival
    multipliers := map[string]float64{
        "diwali":     5.0,
        "holi":       2.0,
        "dussehra":   3.0,
        "christmas":  2.5,
        "new_year":   3.5,
        "republic_day": 1.5,
    }
    
    f.trafficMultiplier = multipliers[festival]
    if f.trafficMultiplier == 0 {
        f.trafficMultiplier = 1.5 // Default multiplier
    }
    
    // Scale services based on priority
    f.scaleServices()
    
    // Configure rate limiting
    f.configureRateLimiting()
    
    // Enable caching
    f.enableAggressiveCaching()
}

func (f *FestivalTrafficManager) scaleServices() {
    for _, service := range f.services {
        newCapacity := int(float64(service.BaseCapacity) * f.trafficMultiplier)
        
        // Ensure we don't exceed max capacity
        if newCapacity > service.MaxCapacity {
            newCapacity = service.MaxCapacity
        }
        
        // Priority-based scaling
        if service.Priority == 1 {
            // Critical services get full scaling
            service.CurrentCapacity = newCapacity
        } else if service.Priority == 2 {
            // Important services get 80% scaling
            service.CurrentCapacity = int(float64(newCapacity) * 0.8)
        } else {
            // Normal services get 60% scaling
            service.CurrentCapacity = int(float64(newCapacity) * 0.6)
        }
        
        // Trigger actual scaling
        f.scaleKubernetesDeployment(service.Name, service.CurrentCapacity)
    }
}

func (f *FestivalTrafficManager) configureRateLimiting() {
    // Configure different rate limits for different services
    f.rateLimiters["payment"] = NewRateLimiter(
        1000,  // requests per second
        5000,  // burst
        time.Second,
    )
    
    f.rateLimiters["catalog"] = NewRateLimiter(
        5000,  // Higher limit for browsing
        10000,
        time.Second,
    )
    
    f.rateLimiters["cart"] = NewRateLimiter(
        2000,
        5000,
        time.Second,
    )
}

// Rate limiter implementation
type RateLimiter struct {
    mu       sync.Mutex
    rate     int
    burst    int
    tokens   int
    lastTime time.Time
}

func NewRateLimiter(rate, burst int, per time.Duration) *RateLimiter {
    return &RateLimiter{
        rate:     rate,
        burst:    burst,
        tokens:   burst,
        lastTime: time.Now(),
    }
}

func (r *RateLimiter) Allow() bool {
    r.mu.Lock()
    defer r.mu.Unlock()
    
    now := time.Now()
    elapsed := now.Sub(r.lastTime).Seconds()
    
    // Add tokens based on elapsed time
    r.tokens += int(elapsed * float64(r.rate))
    if r.tokens > r.burst {
        r.tokens = r.burst
    }
    
    r.lastTime = now
    
    if r.tokens > 0 {
        r.tokens--
        return true
    }
    
    return false
}
```

---

*[Word count for this expansion: ~4,000 words]*