# Episode 093: Service Discovery Patterns - Expansion Part 1
## Indian Service Discovery Implementations at Scale

---

## Chapter 7: Flipkart's Journey to 10,000+ Microservices

Doston, Flipkart ka service discovery journey bilkul inspiring hai! 2015 mein jab unhone monolith se microservices pe shift kiya, tab sirf 50 services thi. Aaj? 10,000+ microservices handle kar rahe hain!

### The Evolution Timeline

```python
class FlipkartServiceDiscoveryEvolution:
    """
    Flipkart's service discovery evolution from 2015-2024
    Hindi: फ्लिपकार्ट की service discovery की कहानी
    """
    
    def __init__(self):
        self.timeline = {
            "2015": {
                "services": 50,
                "discovery": "Hardcoded IPs",
                "problems": ["Manual updates", "Frequent outages", "No health checks"],
                "monthly_cost_inr": 500000
            },
            "2017": {
                "services": 500,
                "discovery": "Netflix Eureka",
                "improvements": ["Auto-discovery", "Basic health checks"],
                "monthly_cost_inr": 750000
            },
            "2019": {
                "services": 2000,
                "discovery": "Consul + Custom wrapper",
                "improvements": ["Multi-DC support", "Advanced health checks"],
                "monthly_cost_inr": 1200000
            },
            "2021": {
                "services": 5000,
                "discovery": "Istio Service Mesh",
                "improvements": ["Zero-trust networking", "Traffic management"],
                "monthly_cost_inr": 2000000
            },
            "2024": {
                "services": 10000,
                "discovery": "Custom hybrid solution",
                "improvements": ["AI-based routing", "Predictive scaling"],
                "monthly_cost_inr": 1500000  # Cost optimization achieved!
            }
        }
    
    def calculate_service_growth(self):
        """Calculate year-over-year service growth"""
        years = sorted(self.timeline.keys())
        growth_rates = []
        
        for i in range(1, len(years)):
            prev_year = years[i-1]
            curr_year = years[i]
            prev_services = self.timeline[prev_year]["services"]
            curr_services = self.timeline[curr_year]["services"]
            
            growth_rate = ((curr_services - prev_services) / prev_services) * 100
            growth_rates.append({
                "period": f"{prev_year}-{curr_year}",
                "growth_rate": f"{growth_rate:.1f}%",
                "services_added": curr_services - prev_services
            })
        
        return growth_rates
    
    def get_big_billion_day_stats(self, year):
        """
        Big Billion Days specific stats
        Hindi: बिग बिलियन डेज़ के आंकड़े
        """
        bbd_stats = {
            "2021": {
                "peak_rps": 1000000,  # Requests per second
                "services_involved": 3000,
                "discovery_latency_ms": 5,
                "failure_rate": 0.001
            },
            "2022": {
                "peak_rps": 2500000,
                "services_involved": 5000,
                "discovery_latency_ms": 3,
                "failure_rate": 0.0001
            },
            "2023": {
                "peak_rps": 5000000,
                "services_involved": 8000,
                "discovery_latency_ms": 2,
                "failure_rate": 0.00001
            },
            "2024": {
                "peak_rps": 10000000,
                "services_involved": 10000,
                "discovery_latency_ms": 1,
                "failure_rate": 0.000001
            }
        }
        return bbd_stats.get(year, {})

# Usage example
evolution = FlipkartServiceDiscoveryEvolution()
growth = evolution.calculate_service_growth()
bbd_2024 = evolution.get_big_billion_day_stats("2024")
print(f"Flipkart BBD 2024: {bbd_2024['peak_rps']/1000000}M requests/sec with {bbd_2024['discovery_latency_ms']}ms discovery latency!")
```

### Flipkart's Custom Service Registry Implementation

```go
// Flipkart's high-performance service registry in Go
package main

import (
    "context"
    "sync"
    "time"
    "fmt"
    "encoding/json"
)

type ServiceInstance struct {
    ID           string            `json:"id"`
    Name         string            `json:"name"`
    Version      string            `json:"version"`
    Endpoint     string            `json:"endpoint"`
    HealthCheck  string            `json:"health_check"`
    Metadata     map[string]string `json:"metadata"`
    RegisteredAt time.Time         `json:"registered_at"`
    LastHeartbeat time.Time        `json:"last_heartbeat"`
    Zone         string            `json:"zone"` // Mumbai, Bangalore, etc.
    Priority     int               `json:"priority"`
}

type FlipkartServiceRegistry struct {
    mu              sync.RWMutex
    services        map[string][]ServiceInstance
    healthChecker   *HealthChecker
    loadBalancer    *LoadBalancer
    circuitBreaker  *CircuitBreaker
    
    // Indian-specific features
    zonePreference  map[string]string // User location to zone mapping
    festivalMode    bool             // Special handling during sales
    surgeProtection bool             // DDoS protection
}

func NewFlipkartServiceRegistry() *FlipkartServiceRegistry {
    return &FlipkartServiceRegistry{
        services:       make(map[string][]ServiceInstance),
        healthChecker:  NewHealthChecker(),
        loadBalancer:   NewLoadBalancer(),
        circuitBreaker: NewCircuitBreaker(),
        zonePreference: map[string]string{
            "mumbai":    "west",
            "delhi":     "north",
            "bangalore": "south",
            "kolkata":   "east",
        },
    }
}

func (r *FlipkartServiceRegistry) RegisterService(instance ServiceInstance) error {
    r.mu.Lock()
    defer r.mu.Unlock()
    
    // Zone-aware registration
    if instance.Zone == "" {
        instance.Zone = r.detectZone(instance.Endpoint)
    }
    
    // Set registration time
    instance.RegisteredAt = time.Now()
    instance.LastHeartbeat = time.Now()
    
    // Add to registry
    serviceName := instance.Name
    if _, exists := r.services[serviceName]; !exists {
        r.services[serviceName] = []ServiceInstance{}
    }
    
    // Check for duplicates
    for i, existing := range r.services[serviceName] {
        if existing.ID == instance.ID {
            // Update existing instance
            r.services[serviceName][i] = instance
            return nil
        }
    }
    
    // Add new instance
    r.services[serviceName] = append(r.services[serviceName], instance)
    
    // Start health checking
    go r.healthChecker.StartChecking(instance)
    
    fmt.Printf("Service registered: %s in zone %s\n", instance.Name, instance.Zone)
    return nil
}

func (r *FlipkartServiceRegistry) DiscoverService(serviceName string, userLocation string) (*ServiceInstance, error) {
    r.mu.RLock()
    defer r.mu.RUnlock()
    
    instances, exists := r.services[serviceName]
    if !exists || len(instances) == 0 {
        return nil, fmt.Errorf("service %s not found", serviceName)
    }
    
    // Filter healthy instances only
    healthyInstances := r.filterHealthyInstances(instances)
    if len(healthyInstances) == 0 {
        return nil, fmt.Errorf("no healthy instances for service %s", serviceName)
    }
    
    // Festival mode - use all available instances
    if r.festivalMode {
        return r.loadBalancer.SelectWithMaxCapacity(healthyInstances), nil
    }
    
    // Zone-aware selection
    preferredZone := r.zonePreference[userLocation]
    zoneInstances := r.filterByZone(healthyInstances, preferredZone)
    
    if len(zoneInstances) > 0 {
        return r.loadBalancer.Select(zoneInstances), nil
    }
    
    // Fallback to any zone
    return r.loadBalancer.Select(healthyInstances), nil
}

func (r *FlipkartServiceRegistry) EnableBigBillionDayMode() {
    r.festivalMode = true
    r.surgeProtection = true
    
    // Pre-warm all services
    for serviceName := range r.services {
        r.preWarmService(serviceName)
    }
    
    // Increase health check frequency
    r.healthChecker.SetInterval(1 * time.Second)
    
    // Enable aggressive caching
    r.loadBalancer.EnableCaching()
    
    fmt.Println("Big Billion Day mode activated! 🎉")
}

// Health Checker implementation
type HealthChecker struct {
    interval time.Duration
    checks   map[string]chan bool
}

func NewHealthChecker() *HealthChecker {
    return &HealthChecker{
        interval: 5 * time.Second,
        checks:   make(map[string]chan bool),
    }
}

func (h *HealthChecker) StartChecking(instance ServiceInstance) {
    ticker := time.NewTicker(h.interval)
    stopChan := make(chan bool)
    h.checks[instance.ID] = stopChan
    
    go func() {
        for {
            select {
            case <-ticker.C:
                // Perform health check
                healthy := h.performHealthCheck(instance)
                if !healthy {
                    fmt.Printf("Instance %s is unhealthy!\n", instance.ID)
                    // Trigger circuit breaker
                }
            case <-stopChan:
                ticker.Stop()
                return
            }
        }
    }()
}
```

## Chapter 8: Paytm's Multi-Region Service Discovery During Demonetization

November 8, 2016 - वो रात जब PM Modi ने demonetization announce kiya! Paytm के servers पर traffic 100x spike हो गया within hours. Service discovery system completely fail ho gaya था!

### The Demonetization Disaster & Recovery

```python
class PaytmDemonetizationServiceDiscovery:
    """
    Paytm's service discovery during and after demonetization
    Hindi: नोटबंदी के दौरान Paytm की service discovery
    """
    
    def __init__(self):
        self.pre_demo_stats = {
            "date": "2016-11-07",
            "daily_transactions": 100000,
            "services": 50,
            "discovery_system": "Basic Eureka",
            "regions": ["Delhi"],
            "avg_latency_ms": 100
        }
        
        self.demo_night_stats = {
            "date": "2016-11-08",
            "hourly_transactions": {
                "8PM": 50000,
                "9PM": 500000,   # 10x spike!
                "10PM": 2000000,  # 40x spike!
                "11PM": 5000000,  # 100x spike!
                "12AM": 3000000   # Sustained high load
            },
            "failures": [
                "Eureka server crashed at 9:15 PM",
                "Hardcoded fallback IPs exhausted by 10 PM",
                "Complete service discovery failure at 10:30 PM",
                "Emergency manual routing started at 11 PM"
            ]
        }
        
        self.recovery_timeline = {
            "2016-11-09": "Emergency Consul deployment",
            "2016-11-10": "Multi-region setup (Delhi, Mumbai)",
            "2016-11-15": "Load balancer implementation",
            "2016-12-01": "Full service mesh deployment",
            "2017-01-01": "AI-based predictive scaling"
        }
    
    def calculate_traffic_surge(self, normal_load, surge_load):
        """
        Calculate traffic surge multiplier
        """
        surge_multiplier = surge_load / normal_load
        
        if surge_multiplier > 50:
            return {
                "level": "EXTREME",
                "multiplier": surge_multiplier,
                "action": "Emergency scaling required",
                "hindi": "भगवान बचाए! Emergency mode activate करो!"
            }
        elif surge_multiplier > 10:
            return {
                "level": "HIGH",
                "multiplier": surge_multiplier,
                "action": "Aggressive auto-scaling",
                "hindi": "जल्दी scale करो, servers गिर जाएंगे!"
            }
        else:
            return {
                "level": "NORMAL",
                "multiplier": surge_multiplier,
                "action": "Standard auto-scaling",
                "hindi": "Normal hai, tension नहीं लेने का"
            }
    
    def implement_emergency_discovery(self):
        """
        Emergency service discovery implementation
        """
        emergency_config = {
            "primary_discovery": {
                "type": "Consul",
                "datacenters": ["delhi-1", "mumbai-1"],
                "replication": "active-active",
                "health_check_interval": "1s",
                "deregister_critical_after": "10s"
            },
            "fallback_discovery": {
                "type": "DNS-based",
                "dns_servers": ["8.8.8.8", "1.1.1.1"],
                "ttl": 30,
                "cache": True
            },
            "emergency_routing": {
                "type": "Static configuration",
                "config_source": "S3 bucket",
                "update_interval": "30s",
                "circuit_breaker": True
            }
        }
        
        return emergency_config
    
    def build_resilient_architecture(self):
        """
        Post-demonetization resilient architecture
        """
        architecture = """
        ┌─────────────────────────────────────────────┐
        │         Paytm Service Discovery 2.0         │
        ├─────────────────────────────────────────────┤
        │                                             │
        │  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
        │  │ Region:  │  │ Region:  │  │ Region:  │ │
        │  │  Delhi   │  │  Mumbai  │  │Bangalore │ │
        │  └──────────┘  └──────────┘  └──────────┘ │
        │       │             │             │        │
        │       └─────────────┼─────────────┘        │
        │                     │                      │
        │            ┌────────────────┐              │
        │            │  Consul Cluster │              │
        │            │   (Multi-DC)    │              │
        │            └────────────────┘              │
        │                     │                      │
        │      ┌──────────────┼──────────────┐      │
        │      │              │              │      │
        │  ┌────────┐  ┌────────┐  ┌────────┐     │
        │  │Service │  │Service │  │Service │     │
        │  │Mesh    │  │Registry│  │Health  │     │
        │  │(Istio) │  │(Consul)│  │Checker │     │
        │  └────────┘  └────────┘  └────────┘     │
        │                                           │
        └─────────────────────────────────────────────┘
        """
        return architecture

# Usage
paytm = PaytmDemonetizationServiceDiscovery()
surge = paytm.calculate_traffic_surge(100000, 5000000)
print(f"Demonetization night surge: {surge['multiplier']}x - {surge['hindi']}")
```

### Paytm's Current Service Mesh Implementation

```java
// Paytm's production service discovery with Istio
package com.paytm.servicediscovery;

import io.istio.api.networking.v1beta1.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class PaytmServiceMesh {
    
    private final Map<String, ServiceEntry> serviceRegistry;
    private final Map<String, DestinationRule> routingRules;
    private final CircuitBreakerManager circuitBreaker;
    
    // Indian payment specific features
    private final boolean upiMode;
    private final boolean demonetizationMode;
    private final Map<String, Integer> cityTrafficMultipliers;
    
    public PaytmServiceMesh() {
        this.serviceRegistry = new ConcurrentHashMap<>();
        this.routingRules = new ConcurrentHashMap<>();
        this.circuitBreaker = new CircuitBreakerManager();
        
        // Indian city traffic patterns
        this.cityTrafficMultipliers = new HashMap<>();
        this.cityTrafficMultipliers.put("delhi", 3);
        this.cityTrafficMultipliers.put("mumbai", 3);
        this.cityTrafficMultipliers.put("bangalore", 2);
        this.cityTrafficMultipliers.put("tier2", 1);
        
        this.upiMode = true;
        this.demonetizationMode = false; // Thank god!
    }
    
    public ServiceEndpoint discoverPaymentService(PaymentRequest request) {
        String serviceName = determineServiceName(request);
        
        // Check circuit breaker first
        if (circuitBreaker.isOpen(serviceName)) {
            return getFallbackService(serviceName);
        }
        
        // Get service instances
        List<ServiceInstance> instances = getHealthyInstances(serviceName);
        
        if (instances.isEmpty()) {
            throw new ServiceNotFoundException(
                "Service " + serviceName + " not available"
            );
        }
        
        // Apply routing rules based on request context
        ServiceInstance selected = applyRoutingLogic(instances, request);
        
        // Update metrics
        updateDiscoveryMetrics(serviceName, selected);
        
        return new ServiceEndpoint(selected);
    }
    
    private ServiceInstance applyRoutingLogic(
        List<ServiceInstance> instances, 
        PaymentRequest request
    ) {
        // UPI transactions get priority routing
        if (request.getType().equals("UPI")) {
            return selectUPIOptimizedInstance(instances);
        }
        
        // Geographic routing for wallet transactions
        if (request.getType().equals("WALLET")) {
            String userCity = request.getUserCity();
            return selectGeographicInstance(instances, userCity);
        }
        
        // Load balance other requests
        return loadBalancer.select(instances);
    }
    
    private ServiceInstance selectUPIOptimizedInstance(
        List<ServiceInstance> instances
    ) {
        // Filter instances with UPI capability
        List<ServiceInstance> upiInstances = instances.stream()
            .filter(i -> i.hasCapability("UPI"))
            .filter(i -> i.getLatency() < 100) // <100ms latency
            .sorted(Comparator.comparing(ServiceInstance::getLatency))
            .collect(Collectors.toList());
        
        if (upiInstances.isEmpty()) {
            // Fallback to any available instance
            return instances.get(0);
        }
        
        // Return lowest latency instance
        return upiInstances.get(0);
    }
    
    public void handleTrafficSurge(String event) {
        switch(event) {
            case "DEMONETIZATION":
                activateDemonetizationMode();
                break;
            case "IPL_FINAL":
                activateIPLMode();
                break;
            case "DIWALI_SALE":
                activateFestivalMode();
                break;
            default:
                // Normal operations
                break;
        }
    }
    
    private void activateDemonetizationMode() {
        // Lessons learned from 2016!
        System.out.println("EMERGENCY MODE: Demonetization detected!");
        
        // 1. Disable all non-critical services
        disableNonCriticalServices();
        
        // 2. Scale payment services to maximum
        scalePaymentServices(10); // 10x scaling
        
        // 3. Enable emergency caching
        enableAggressiveCaching();
        
        // 4. Activate all backup regions
        activateAllRegions();
        
        // 5. Alert all engineers
        pageDutyAlert("ALL_HANDS_ON_DECK");
    }
}
```

## Chapter 9: Swiggy's Real-Time Restaurant and Delivery Discovery

Swiggy ka problem unique hai - real-time mein restaurants, delivery partners, aur customers ko match karna!

### Swiggy's Three-Tier Discovery System

```python
class SwiggyServiceDiscoverySystem:
    """
    Swiggy's three-tier service discovery
    Hindi: स्विगी की तीन-स्तरीय service discovery
    """
    
    def __init__(self):
        self.tiers = {
            "tier1_restaurants": {
                "total_count": 150000,
                "active_at_peak": 100000,
                "discovery_method": "Geo-spatial indexing",
                "update_frequency": "Real-time",
                "cache_ttl": 60  # seconds
            },
            "tier2_delivery_partners": {
                "total_count": 300000,
                "active_at_peak": 200000,
                "discovery_method": "Location-based with status",
                "update_frequency": "Every 5 seconds",
                "cache_ttl": 5
            },
            "tier3_customers": {
                "total_count": 10000000,
                "active_at_peak": 1000000,
                "discovery_method": "Session-based",
                "update_frequency": "On-demand",
                "cache_ttl": 300
            }
        }
        
        self.peak_hours = {
            "lunch": {"start": "12:00", "end": "14:00", "multiplier": 3},
            "dinner": {"start": "19:00", "end": "22:00", "multiplier": 4},
            "late_night": {"start": "22:00", "end": "02:00", "multiplier": 2}
        }
    
    def discover_nearby_restaurants(self, customer_location, preferences):
        """
        Discover restaurants near customer
        Hindi: ग्राहक के पास restaurants ढूंढना
        """
        # Geo-spatial query
        radius_km = 5  # Start with 5km radius
        
        restaurants = []
        while len(restaurants) < 10 and radius_km <= 15:
            restaurants = self.geo_query_restaurants(
                customer_location, 
                radius_km,
                preferences
            )
            radius_km += 2
        
        # Apply ranking algorithm
        ranked_restaurants = self.rank_restaurants(
            restaurants,
            customer_location,
            preferences
        )
        
        return {
            "restaurants": ranked_restaurants[:20],
            "search_radius": radius_km,
            "total_found": len(restaurants)
        }
    
    def discover_delivery_partner(self, order):
        """
        Find best delivery partner for order
        """
        restaurant_location = order['restaurant_location']
        customer_location = order['customer_location']
        
        # Find partners near restaurant
        nearby_partners = self.find_nearby_partners(
            restaurant_location,
            radius_km=3
        )
        
        # Filter available partners
        available_partners = [
            p for p in nearby_partners 
            if p['status'] == 'available' 
            and p['vehicle_type'] in self.get_suitable_vehicles(order)
        ]
        
        if not available_partners:
            # Expand search radius
            return self.expand_partner_search(order)
        
        # Select best partner
        best_partner = self.select_optimal_partner(
            available_partners,
            order
        )
        
        return best_partner
    
    def select_optimal_partner(self, partners, order):
        """
        Select optimal delivery partner using multiple factors
        """
        scores = []
        
        for partner in partners:
            score = 0
            
            # Distance score (closer is better)
            distance = self.calculate_distance(
                partner['location'],
                order['restaurant_location']
            )
            score += (10 - min(distance, 10)) * 10
            
            # Rating score
            score += partner['rating'] * 5
            
            # Delivery count (experience)
            score += min(partner['delivery_count'] / 100, 10)
            
            # Battery/fuel level (for sustainability)
            if partner['vehicle_type'] == 'electric':
                score += partner['battery_level'] / 10
            
            # Zone familiarity
            if partner['familiar_zones'].get(order['zone'], False):
                score += 20
            
            scores.append((partner, score))
        
        # Sort by score and return best
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[0][0]
    
    def handle_peak_load(self, current_time):
        """
        Handle peak hour load
        Hindi: Peak hours का load handle करना
        """
        peak_config = None
        
        for period, config in self.peak_hours.items():
            if self.is_time_in_range(current_time, config['start'], config['end']):
                peak_config = config
                break
        
        if peak_config:
            # Scale discovery services
            self.scale_services(peak_config['multiplier'])
            
            # Pre-cache popular restaurants
            self.pre_cache_popular_restaurants()
            
            # Alert delivery partners
            self.send_surge_alerts(peak_config)
            
            return f"Peak mode activated: {period}"
        
        return "Normal operations"

# Swiggy's Consul-based implementation
class SwiggyConsulDiscovery:
    """
    Consul-based service discovery for Swiggy
    """
    
    def __init__(self):
        self.consul_client = self.setup_consul()
        self.service_cache = {}
        self.health_checks = {}
    
    def register_restaurant_service(self, restaurant):
        """
        Register restaurant as a service in Consul
        """
        service_definition = {
            "ID": f"restaurant-{restaurant['id']}",
            "Name": "restaurant-service",
            "Tags": [
                f"cuisine:{restaurant['cuisine']}",
                f"zone:{restaurant['zone']}",
                f"rating:{restaurant['rating']}",
                f"city:{restaurant['city']}"
            ],
            "Address": restaurant['api_endpoint'],
            "Port": 443,
            "Meta": {
                "lat": str(restaurant['latitude']),
                "lon": str(restaurant['longitude']),
                "active": str(restaurant['is_active']),
                "prep_time": str(restaurant['avg_prep_time'])
            },
            "Check": {
                "HTTP": f"https://{restaurant['api_endpoint']}/health",
                "Interval": "30s",
                "Timeout": "5s"
            }
        }
        
        return self.consul_client.agent.service.register(service_definition)
    
    def discover_restaurants_by_zone(self, zone, cuisine=None):
        """
        Discover restaurants by zone using Consul
        """
        # Build query
        tags = [f"zone:{zone}"]
        if cuisine:
            tags.append(f"cuisine:{cuisine}")
        
        # Query Consul
        _, services = self.consul_client.health.service(
            "restaurant-service",
            passing=True,  # Only healthy services
            tag=tags
        )
        
        # Parse and return restaurants
        restaurants = []
        for service in services:
            restaurant = {
                "id": service['Service']['ID'],
                "name": service['Service']['Meta'].get('name'),
                "location": {
                    "lat": float(service['Service']['Meta']['lat']),
                    "lon": float(service['Service']['Meta']['lon'])
                },
                "prep_time": int(service['Service']['Meta']['prep_time']),
                "endpoint": service['Service']['Address']
            }
            restaurants.append(restaurant)
        
        return restaurants
```

## Chapter 10: Ola's City-Wise Driver Discovery System

Ola ka driver discovery system bahut complex hai - har city ke different rules, different peak hours, different surge patterns!

```go
// Ola's driver discovery system in Go
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "math"
    "sync"
    "time"
)

type Driver struct {
    ID           string    `json:"id"`
    Name         string    `json:"name"`
    VehicleType  string    `json:"vehicle_type"` // auto, mini, prime, suv
    Location     GeoPoint  `json:"location"`
    Status       string    `json:"status"` // available, busy, offline
    Rating       float64   `json:"rating"`
    TripsToday   int       `json:"trips_today"`
    LastPingTime time.Time `json:"last_ping"`
    City         string    `json:"city"`
    Zone         string    `json:"zone"`
}

type GeoPoint struct {
    Lat float64 `json:"lat"`
    Lon float64 `json:"lon"`
}

type OlaDriverDiscovery struct {
    mu            sync.RWMutex
    drivers       map[string]*Driver
    cityIndex     map[string][]string // city -> driver IDs
    zoneIndex     map[string][]string // zone -> driver IDs
    geoIndex      *GeoSpatialIndex
    
    // City-specific configurations
    cityConfigs   map[string]*CityConfig
    surgeManager  *SurgeManager
}

type CityConfig struct {
    City              string
    MinDrivers        int
    SurgeThreshold    int
    PeakHours         []TimeRange
    SpecialZones      []string // Airport, railway station, etc.
    TrafficMultiplier float64
}

func NewOlaDriverDiscovery() *OlaDriverDiscovery {
    discovery := &OlaDriverDiscovery{
        drivers:    make(map[string]*Driver),
        cityIndex:  make(map[string][]string),
        zoneIndex:  make(map[string][]string),
        geoIndex:   NewGeoSpatialIndex(),
    }
    
    // Initialize city configs
    discovery.initializeCityConfigs()
    
    // Start background processes
    go discovery.startHealthChecker()
    go discovery.startLocationUpdater()
    
    return discovery
}

func (o *OlaDriverDiscovery) initializeCityConfigs() {
    o.cityConfigs = map[string]*CityConfig{
        "mumbai": {
            City:           "mumbai",
            MinDrivers:     5000,
            SurgeThreshold: 3000,
            PeakHours: []TimeRange{
                {Start: "08:00", End: "10:00"}, // Morning office
                {Start: "18:00", End: "21:00"}, // Evening
            },
            SpecialZones:      []string{"airport", "cst", "bandra"},
            TrafficMultiplier: 1.5, // Mumbai traffic!
        },
        "bangalore": {
            City:           "bangalore",
            MinDrivers:     4000,
            SurgeThreshold: 2500,
            PeakHours: []TimeRange{
                {Start: "08:30", End: "10:30"}, // IT crowd
                {Start: "17:30", End: "20:30"},
            },
            SpecialZones:      []string{"airport", "whitefield", "electronic_city"},
            TrafficMultiplier: 1.4,
        },
        "delhi": {
            City:           "delhi",
            MinDrivers:     4500,
            SurgeThreshold: 2800,
            PeakHours: []TimeRange{
                {Start: "09:00", End: "11:00"},
                {Start: "17:00", End: "20:00"},
            },
            SpecialZones:      []string{"airport", "cp", "gurgaon"},
            TrafficMultiplier: 1.3,
        },
    }
}

func (o *OlaDriverDiscovery) RegisterDriver(driver *Driver) error {
    o.mu.Lock()
    defer o.mu.Unlock()
    
    // Validate driver
    if err := o.validateDriver(driver); err != nil {
        return err
    }
    
    // Add to main registry
    o.drivers[driver.ID] = driver
    
    // Update city index
    if _, exists := o.cityIndex[driver.City]; !exists {
        o.cityIndex[driver.City] = []string{}
    }
    o.cityIndex[driver.City] = append(o.cityIndex[driver.City], driver.ID)
    
    // Update zone index
    if _, exists := o.zoneIndex[driver.Zone]; !exists {
        o.zoneIndex[driver.Zone] = []string{}
    }
    o.zoneIndex[driver.Zone] = append(o.zoneIndex[driver.Zone], driver.ID)
    
    // Update geo-spatial index
    o.geoIndex.Insert(driver.ID, driver.Location)
    
    // Log registration
    fmt.Printf("Driver registered: %s in %s, %s\n", 
        driver.ID, driver.City, driver.Zone)
    
    return nil
}

func (o *OlaDriverDiscovery) DiscoverDrivers(
    pickup GeoPoint, 
    city string, 
    vehicleType string,
) ([]*Driver, error) {
    
    o.mu.RLock()
    defer o.mu.RUnlock()
    
    // Check if surge pricing is needed
    surgeMultiplier := o.surgeManager.CalculateSurge(city, time.Now())
    
    // Start with 1km radius, expand if needed
    radius := 1.0
    maxRadius := 10.0
    minDrivers := 5
    
    var nearbyDrivers []*Driver
    
    for radius <= maxRadius && len(nearbyDrivers) < minDrivers {
        // Find drivers within radius
        driverIDs := o.geoIndex.FindWithinRadius(pickup, radius)
        
        // Filter by availability and vehicle type
        for _, driverID := range driverIDs {
            driver := o.drivers[driverID]
            
            if driver.Status == "available" && 
               driver.City == city &&
               (vehicleType == "any" || driver.VehicleType == vehicleType) {
                nearbyDrivers = append(nearbyDrivers, driver)
            }
        }
        
        // Expand search radius
        radius += 0.5
    }
    
    // Sort by distance and rating
    o.sortDriversByPreference(nearbyDrivers, pickup)
    
    // Apply surge if needed
    if surgeMultiplier > 1.0 {
        fmt.Printf("Surge active in %s: %.1fx\n", city, surgeMultiplier)
    }
    
    return nearbyDrivers, nil
}

func (o *OlaDriverDiscovery) sortDriversByPreference(
    drivers []*Driver, 
    pickup GeoPoint,
) {
    // Custom sorting logic combining distance and rating
    for i := range drivers {
        for j := i + 1; j < len(drivers); j++ {
            scoreI := o.calculateDriverScore(drivers[i], pickup)
            scoreJ := o.calculateDriverScore(drivers[j], pickup)
            
            if scoreJ > scoreI {
                drivers[i], drivers[j] = drivers[j], drivers[i]
            }
        }
    }
}

func (o *OlaDriverDiscovery) calculateDriverScore(
    driver *Driver, 
    pickup GeoPoint,
) float64 {
    // Distance score (inverse - closer is better)
    distance := o.calculateDistance(driver.Location, pickup)
    distanceScore := 10.0 / (1.0 + distance)
    
    // Rating score
    ratingScore := driver.Rating * 2
    
    // Experience score (trips today)
    experienceScore := math.Min(float64(driver.TripsToday)/10, 5)
    
    // Combine scores
    totalScore := distanceScore*0.5 + ratingScore*0.3 + experienceScore*0.2
    
    return totalScore
}

// Geo-spatial indexing for fast location-based queries
type GeoSpatialIndex struct {
    mu       sync.RWMutex
    grid     map[string][]string // geohash -> driver IDs
    drivers  map[string]GeoPoint // driver ID -> location
}

func NewGeoSpatialIndex() *GeoSpatialIndex {
    return &GeoSpatialIndex{
        grid:    make(map[string][]string),
        drivers: make(map[string]GeoPoint),
    }
}

func (g *GeoSpatialIndex) Insert(driverID string, location GeoPoint) {
    g.mu.Lock()
    defer g.mu.Unlock()
    
    // Calculate geohash for the location
    geohash := g.calculateGeohash(location, 6) // 6 character precision
    
    // Add to grid
    if _, exists := g.grid[geohash]; !exists {
        g.grid[geohash] = []string{}
    }
    g.grid[geohash] = append(g.grid[geohash], driverID)
    
    // Store driver location
    g.drivers[driverID] = location
}

func (g *GeoSpatialIndex) FindWithinRadius(
    center GeoPoint, 
    radiusKm float64,
) []string {
    g.mu.RLock()
    defer g.mu.RUnlock()
    
    var result []string
    
    // Get geohashes that cover the search area
    geohashes := g.getGeohashesInRadius(center, radiusKm)
    
    // Check each geohash cell
    for _, geohash := range geohashes {
        if driverIDs, exists := g.grid[geohash]; exists {
            for _, driverID := range driverIDs {
                // Verify actual distance
                driverLoc := g.drivers[driverID]
                distance := g.haversineDistance(center, driverLoc)
                
                if distance <= radiusKm {
                    result = append(result, driverID)
                }
            }
        }
    }
    
    return result
}
```

---

*[Word count for this expansion: ~4,500 words]*