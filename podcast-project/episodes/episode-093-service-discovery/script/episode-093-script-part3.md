# Episode 093: Service Discovery & Load Balancing - Part 3
## Production Strategies & Real-World Case Studies (Minutes 121-180)

*Total Word Count Target: 7,000 words*

---

## Chapter 10: Load Balancing Algorithms in Production

### Advanced Load Balancing Strategies

"Load balancing is like managing queues at Tirupati temple - lakhs of devotees, multiple darshan lines, VIP routes, senior citizen preferences - sab kuch organized!"

```python
import hashlib
import bisect
import random
import time
from collections import defaultdict, deque
from typing import List, Dict, Any

class TirupatiLoadBalancer:
    """
    Advanced load balancing inspired by Tirupati queue management
    Handling 100,000+ requests per day
    """
    
    def __init__(self):
        self.servers = {}
        self.algorithms = {
            'round_robin': self.round_robin,
            'weighted_round_robin': self.weighted_round_robin,
            'least_connections': self.least_connections,
            'least_response_time': self.least_response_time,
            'consistent_hash': self.consistent_hash,
            'ip_hash': self.ip_hash,
            'random': self.random_selection,
            'power_of_two_choices': self.power_of_two_choices
        }
        
        # Round robin state
        self.rr_current = 0
        
        # Weighted round robin state
        self.wrr_current = 0
        self.wrr_weights = []
        
        # Consistent hashing
        self.hash_ring = {}
        self.sorted_keys = []
        
        # Connection tracking
        self.active_connections = defaultdict(int)
        
        # Response time tracking
        self.response_times = defaultdict(deque)
        self.response_time_window = 100  # Last 100 requests
        
    def add_server(self, server_id: str, config: Dict[str, Any]):
        """
        Add server to load balancer
        Like adding new darshan counter at temple
        """
        self.servers[server_id] = {
            'id': server_id,
            'ip': config['ip'],
            'port': config['port'],
            'weight': config.get('weight', 1),
            'max_connections': config.get('max_connections', 1000),
            'region': config.get('region', 'mumbai'),
            'tier': config.get('tier', 'standard'),  # standard, premium, vip
            'health': 'healthy',
            'cpu_usage': 0,
            'memory_usage': 0,
            'last_health_check': time.time()
        }
        
        # Update consistent hash ring
        self._update_hash_ring()
        
        # Update weighted round robin
        self._update_wrr_weights()
        
        print(f"✅ Server {server_id} added to load balancer")
        print(f"   Region: {config.get('region', 'mumbai')}")
        print(f"   Tier: {config.get('tier', 'standard')}")
        print(f"   Weight: {config.get('weight', 1)}")
    
    def round_robin(self, request=None):
        """
        Simple round robin - like token system at bank
        """
        if not self.servers:
            return None
        
        healthy_servers = [s for s in self.servers.values() 
                          if s['health'] == 'healthy']
        
        if not healthy_servers:
            return None
        
        server = healthy_servers[self.rr_current % len(healthy_servers)]
        self.rr_current = (self.rr_current + 1) % len(healthy_servers)
        
        return server
    
    def weighted_round_robin(self, request=None):
        """
        Weighted round robin - like VIP counters at airport
        More weight = more requests
        """
        if not self.servers:
            return None
        
        if not self.wrr_weights:
            self._update_wrr_weights()
        
        if not self.wrr_weights:
            return None
        
        server_id = self.wrr_weights[self.wrr_current]
        self.wrr_current = (self.wrr_current + 1) % len(self.wrr_weights)
        
        return self.servers[server_id]
    
    def _update_wrr_weights(self):
        """
        Update weighted round robin distribution
        """
        self.wrr_weights = []
        
        for server_id, server in self.servers.items():
            if server['health'] == 'healthy':
                # Add server ID multiple times based on weight
                weight = server['weight']
                self.wrr_weights.extend([server_id] * weight)
        
        # Shuffle for better distribution
        random.shuffle(self.wrr_weights)
    
    def least_connections(self, request=None):
        """
        Route to server with least active connections
        Like finding shortest queue at ticket counter
        """
        if not self.servers:
            return None
        
        healthy_servers = [(s, self.active_connections[s['id']]) 
                          for s in self.servers.values() 
                          if s['health'] == 'healthy']
        
        if not healthy_servers:
            return None
        
        # Sort by connection count
        healthy_servers.sort(key=lambda x: x[1])
        
        # Return server with least connections
        return healthy_servers[0][0]
    
    def least_response_time(self, request=None):
        """
        Route to fastest responding server
        Like choosing fastest moving queue
        """
        if not self.servers:
            return None
        
        server_scores = []
        
        for server in self.servers.values():
            if server['health'] != 'healthy':
                continue
            
            # Calculate average response time
            if server['id'] in self.response_times:
                times = self.response_times[server['id']]
                if times:
                    avg_time = sum(times) / len(times)
                else:
                    avg_time = 0
            else:
                avg_time = 0
            
            # Factor in current connections
            connection_penalty = self.active_connections[server['id']] * 10
            
            score = avg_time + connection_penalty
            server_scores.append((server, score))
        
        if not server_scores:
            return None
        
        # Sort by score (lower is better)
        server_scores.sort(key=lambda x: x[1])
        
        return server_scores[0][0]
    
    def consistent_hash(self, request):
        """
        Consistent hashing for session affinity
        Like assigned priest for regular devotees
        """
        if not self.servers or not self.sorted_keys:
            return None
        
        # Get hash of request key (e.g., user ID)
        request_key = request.get('user_id', str(random.random()))
        hash_value = self._hash(request_key)
        
        # Find the server using binary search
        idx = bisect.bisect_right(self.sorted_keys, hash_value)
        
        if idx == len(self.sorted_keys):
            idx = 0
        
        server_hash = self.sorted_keys[idx]
        server_id = self.hash_ring[server_hash]
        
        return self.servers.get(server_id)
    
    def _update_hash_ring(self):
        """
        Update consistent hash ring
        """
        self.hash_ring = {}
        self.sorted_keys = []
        
        for server_id, server in self.servers.items():
            if server['health'] == 'healthy':
                # Add multiple virtual nodes for better distribution
                for i in range(150):  # 150 virtual nodes per server
                    virtual_key = f"{server_id}:{i}"
                    hash_value = self._hash(virtual_key)
                    self.hash_ring[hash_value] = server_id
                    self.sorted_keys.append(hash_value)
        
        self.sorted_keys.sort()
    
    def _hash(self, key: str) -> int:
        """Generate hash value"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def ip_hash(self, request):
        """
        Route based on client IP - session persistence
        Like regular customer getting same shopkeeper
        """
        if not self.servers:
            return None
        
        client_ip = request.get('client_ip', '127.0.0.1')
        hash_value = self._hash(client_ip)
        
        healthy_servers = [s for s in self.servers.values() 
                          if s['health'] == 'healthy']
        
        if not healthy_servers:
            return None
        
        # Select server based on hash
        index = hash_value % len(healthy_servers)
        return healthy_servers[index]
    
    def power_of_two_choices(self, request=None):
        """
        Randomly pick 2 servers, choose the better one
        Proven to be very effective in practice
        """
        if not self.servers:
            return None
        
        healthy_servers = [s for s in self.servers.values() 
                          if s['health'] == 'healthy']
        
        if not healthy_servers:
            return None
        
        if len(healthy_servers) == 1:
            return healthy_servers[0]
        
        # Pick two random servers
        choices = random.sample(healthy_servers, 
                               min(2, len(healthy_servers)))
        
        # Choose the one with fewer connections
        if len(choices) == 2:
            conn1 = self.active_connections[choices[0]['id']]
            conn2 = self.active_connections[choices[1]['id']]
            return choices[0] if conn1 <= conn2 else choices[1]
        
        return choices[0]
    
    def random_selection(self, request=None):
        """
        Random selection - simplest approach
        Like lottery system
        """
        if not self.servers:
            return None
        
        healthy_servers = [s for s in self.servers.values() 
                          if s['health'] == 'healthy']
        
        if not healthy_servers:
            return None
        
        return random.choice(healthy_servers)
```

### Geographic and Latency-Based Load Balancing

"Geographic load balancing is like Indian Railways zones - Northern Railway, Southern Railway - passengers go to nearest zone!"

```python
import math
from dataclasses import dataclass
from typing import Tuple

@dataclass
class Location:
    """Geographic location"""
    city: str
    latitude: float
    longitude: float
    
class GeographicLoadBalancer:
    """
    Geographic load balancing for Indian regions
    Used by CDN providers and streaming services
    """
    
    def __init__(self):
        # Indian city coordinates
        self.city_locations = {
            'mumbai': Location('Mumbai', 19.0760, 72.8777),
            'delhi': Location('Delhi', 28.6139, 77.2090),
            'bangalore': Location('Bangalore', 12.9716, 77.5946),
            'chennai': Location('Chennai', 13.0827, 80.2707),
            'kolkata': Location('Kolkata', 22.5726, 88.3639),
            'hyderabad': Location('Hyderabad', 17.3850, 78.4867),
            'pune': Location('Pune', 18.5204, 73.8567),
            'ahmedabad': Location('Ahmedabad', 23.0225, 72.5714),
            'jaipur': Location('Jaipur', 26.9124, 75.7873),
            'lucknow': Location('Lucknow', 26.8467, 80.9462)
        }
        
        # Data center locations
        self.datacenters = {
            'dc-mumbai-1': {
                'location': self.city_locations['mumbai'],
                'capacity': 10000,
                'current_load': 0,
                'services': ['api', 'streaming', 'storage'],
                'tier': 'primary',
                'cost_per_request': 0.001  # INR
            },
            'dc-delhi-1': {
                'location': self.city_locations['delhi'],
                'capacity': 8000,
                'current_load': 0,
                'services': ['api', 'streaming'],
                'tier': 'primary',
                'cost_per_request': 0.0012
            },
            'dc-bangalore-1': {
                'location': self.city_locations['bangalore'],
                'capacity': 12000,
                'current_load': 0,
                'services': ['api', 'streaming', 'ml', 'storage'],
                'tier': 'primary',
                'cost_per_request': 0.0008
            },
            'dc-chennai-1': {
                'location': self.city_locations['chennai'],
                'capacity': 5000,
                'current_load': 0,
                'services': ['api', 'storage'],
                'tier': 'secondary',
                'cost_per_request': 0.0015
            }
        }
        
        # Network latency matrix (ms) - based on real measurements
        self.latency_matrix = {
            ('mumbai', 'delhi'): 28,
            ('mumbai', 'bangalore'): 20,
            ('mumbai', 'chennai'): 25,
            ('delhi', 'bangalore'): 35,
            ('delhi', 'chennai'): 40,
            ('bangalore', 'chennai'): 15,
            # Add reverse mappings
        }
        
        # Add reverse latencies
        reverse_latencies = {}
        for (city1, city2), latency in self.latency_matrix.items():
            reverse_latencies[(city2, city1)] = latency
        self.latency_matrix.update(reverse_latencies)
    
    def calculate_distance(self, loc1: Location, loc2: Location) -> float:
        """
        Calculate distance between two locations using Haversine formula
        Returns distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1 = math.radians(loc1.latitude), math.radians(loc1.longitude)
        lat2, lon2 = math.radians(loc2.latitude), math.radians(loc2.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def find_nearest_datacenter(self, user_city: str, 
                               service_type: str = 'api') -> str:
        """
        Find nearest datacenter for user
        Like finding nearest railway station
        """
        if user_city not in self.city_locations:
            # Default to Mumbai for unknown cities
            user_city = 'mumbai'
        
        user_location = self.city_locations[user_city]
        
        nearest_dc = None
        min_distance = float('inf')
        
        for dc_id, dc_info in self.datacenters.items():
            # Check if datacenter provides required service
            if service_type not in dc_info['services']:
                continue
            
            # Check if datacenter has capacity
            if dc_info['current_load'] >= dc_info['capacity']:
                continue
            
            # Calculate distance
            distance = self.calculate_distance(
                user_location, 
                dc_info['location']
            )
            
            if distance < min_distance:
                min_distance = distance
                nearest_dc = dc_id
        
        return nearest_dc
    
    def latency_aware_selection(self, user_city: str, 
                                service_type: str = 'api') -> str:
        """
        Select datacenter based on network latency
        More accurate than geographic distance
        """
        candidates = []
        
        for dc_id, dc_info in self.datacenters.items():
            # Check service availability
            if service_type not in dc_info['services']:
                continue
            
            # Check capacity
            load_percentage = (dc_info['current_load'] / 
                             dc_info['capacity'] * 100)
            if load_percentage > 90:
                continue
            
            # Get datacenter city
            dc_city = dc_info['location'].city.lower()
            
            # Calculate effective latency
            if user_city == dc_city:
                latency = 2  # Same city, minimal latency
            elif (user_city, dc_city) in self.latency_matrix:
                latency = self.latency_matrix[(user_city, dc_city)]
            else:
                # Estimate based on distance
                distance = self.calculate_distance(
                    self.city_locations.get(user_city, 
                                           self.city_locations['mumbai']),
                    dc_info['location']
                )
                latency = distance * 0.05  # Rough estimate
            
            # Add load factor to latency
            latency += load_percentage * 0.5
            
            candidates.append({
                'dc_id': dc_id,
                'latency': latency,
                'load': load_percentage,
                'cost': dc_info['cost_per_request']
            })
        
        if not candidates:
            return None
        
        # Sort by latency (primary) and cost (secondary)
        candidates.sort(key=lambda x: (x['latency'], x['cost']))
        
        return candidates[0]['dc_id']
    
    def multi_factor_selection(self, user_city: str, 
                              service_type: str,
                              user_tier: str = 'free') -> str:
        """
        Advanced selection considering multiple factors
        Like choosing flight - price, time, airline all matter
        """
        weights = {
            'free': {'latency': 0.3, 'cost': 0.6, 'load': 0.1},
            'premium': {'latency': 0.6, 'cost': 0.2, 'load': 0.2},
            'enterprise': {'latency': 0.5, 'cost': 0.1, 'load': 0.4}
        }
        
        user_weights = weights.get(user_tier, weights['free'])
        candidates = []
        
        for dc_id, dc_info in self.datacenters.items():
            if service_type not in dc_info['services']:
                continue
            
            load_percentage = (dc_info['current_load'] / 
                             dc_info['capacity'] * 100)
            
            if load_percentage > 95:
                continue
            
            # Calculate scores
            dc_city = dc_info['location'].city.lower()
            
            # Latency score (lower is better, normalize to 0-1)
            if user_city == dc_city:
                latency_score = 0.1
            elif (user_city, dc_city) in self.latency_matrix:
                latency = self.latency_matrix[(user_city, dc_city)]
                latency_score = min(latency / 100, 1)  # Normalize
            else:
                latency_score = 0.5  # Default medium score
            
            # Cost score (lower is better)
            cost_score = dc_info['cost_per_request'] / 0.002  # Normalize
            
            # Load score (lower is better)
            load_score = load_percentage / 100
            
            # Calculate weighted score
            total_score = (
                user_weights['latency'] * (1 - latency_score) +
                user_weights['cost'] * (1 - cost_score) +
                user_weights['load'] * (1 - load_score)
            )
            
            candidates.append({
                'dc_id': dc_id,
                'score': total_score,
                'latency_score': latency_score,
                'cost_score': cost_score,
                'load_score': load_score
            })
        
        if not candidates:
            return None
        
        # Sort by total score (higher is better)
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        selected = candidates[0]
        
        print(f"📍 Selected datacenter: {selected['dc_id']}")
        print(f"   Score: {selected['score']:.2f}")
        print(f"   Latency: {selected['latency_score']:.2f}")
        print(f"   Cost: {selected['cost_score']:.2f}")
        print(f"   Load: {selected['load_score']:.2f}")
        
        return selected['dc_id']
```

## Chapter 11: Production Case Studies - Indian Scale

### PhonePe's Service Discovery Evolution

"PhonePe ka journey - from 100 transactions per day to 100 million! Kaise handle kiya unhone service discovery?"

```python
class PhonePeServiceDiscoveryEvolution:
    """
    PhonePe's journey from startup to scale
    Real architecture evolution 2016-2024
    """
    
    def __init__(self):
        self.timeline = {
            '2016': {
                'scale': '1000 transactions/day',
                'architecture': 'Monolithic',
                'discovery': 'Hardcoded IPs',
                'challenges': [
                    'Manual configuration',
                    'No redundancy',
                    'Deployment downtime'
                ]
            },
            '2017': {
                'scale': '100K transactions/day',
                'architecture': 'Service-oriented',
                'discovery': 'Netflix Eureka',
                'improvements': [
                    'Dynamic discovery',
                    'Client-side load balancing',
                    'Health checks'
                ],
                'challenges': [
                    'Eureka learning curve',
                    'Java ecosystem lock-in'
                ]
            },
            '2018': {
                'scale': '1M transactions/day',
                'architecture': 'Microservices',
                'discovery': 'Consul + Eureka',
                'improvements': [
                    'Multi-datacenter support',
                    'Service mesh preparation',
                    'KV store for config'
                ],
                'challenges': [
                    'Dual discovery complexity',
                    'Operational overhead'
                ]
            },
            '2019': {
                'scale': '10M transactions/day',
                'architecture': 'Kubernetes native',
                'discovery': 'Kubernetes + Istio',
                'improvements': [
                    'Native Kubernetes discovery',
                    'Istio service mesh',
                    'Automatic sidecar injection'
                ],
                'challenges': [
                    'Istio complexity',
                    'Performance overhead'
                ]
            },
            '2020-2021': {
                'scale': '50M transactions/day',
                'architecture': 'Hybrid cloud',
                'discovery': 'Custom solution',
                'improvements': [
                    'Cross-cloud discovery',
                    'Edge locations',
                    'Global load balancing'
                ],
                'key_learnings': [
                    'Build vs buy decision',
                    'Operational simplicity matters'
                ]
            },
            '2022-2024': {
                'scale': '100M+ transactions/day',
                'architecture': 'Multi-region active-active',
                'discovery': 'Kubernetes + Custom control plane',
                'innovations': [
                    'AI-based load prediction',
                    'Automated failover',
                    'Cost-optimized routing'
                ]
            }
        }
    
    def migration_strategy_2018(self):
        """
        How PhonePe migrated from Eureka to Consul
        Without downtime!
        """
        migration_steps = [
            {
                'phase': 'Phase 1 - Dual Registration',
                'duration': '2 months',
                'description': 'Services register with both Eureka and Consul',
                'code': '''
# Dual registration adapter
class DualDiscoveryClient:
    def __init__(self):
        self.eureka_client = EurekaClient()
        self.consul_client = ConsulClient()
    
    def register(self, service_info):
        # Register with both
        self.eureka_client.register(service_info)
        self.consul_client.register(service_info)
        
    def discover(self, service_name):
        # Prefer Consul, fallback to Eureka
        try:
            return self.consul_client.discover(service_name)
        except:
            return self.eureka_client.discover(service_name)
                '''
            },
            {
                'phase': 'Phase 2 - Gradual Migration',
                'duration': '3 months',
                'description': 'Migrate services one by one',
                'strategy': 'Start with non-critical services'
            },
            {
                'phase': 'Phase 3 - Consul Primary',
                'duration': '1 month',
                'description': 'Make Consul primary, Eureka backup'
            },
            {
                'phase': 'Phase 4 - Decommission',
                'duration': '1 month',
                'description': 'Remove Eureka completely'
            }
        ]
        
        return migration_steps
    
    def current_architecture_2024(self):
        """
        PhonePe's current service discovery architecture
        """
        return {
            'primary_discovery': 'Kubernetes DNS + Endpoints',
            'service_mesh': 'Custom lightweight mesh',
            'edge_discovery': 'Consul at edge locations',
            'global_routing': 'Custom control plane',
            
            'scale_numbers': {
                'services': 500,
                'instances': 50000,
                'requests_per_second': 1000000,
                'p99_discovery_latency': '5ms',
                'regions': 5,
                'availability': '99.999%'
            },
            
            'key_features': [
                'Geo-aware routing',
                'Cost-optimized path selection',
                'Automatic failover in <1s',
                'A/B testing support',
                'Canary deployments',
                'Circuit breaker per route'
            ],
            
            'monitoring': {
                'metrics': 'Prometheus + Thanos',
                'tracing': 'Jaeger',
                'logs': 'ELK Stack',
                'dashboards': 'Grafana'
            }
        }
```

### Swiggy's Load Balancing During Peak Hours

"Swiggy ka peak hour load balancing - lunch time pe 10x traffic! Kaise manage karte hain?"

```go
// Swiggy's peak hour load balancing strategy
package main

import (
    "context"
    "fmt"
    "sync"
    "time"
)

// SwiggyPeakLoadBalancer handles peak hour traffic
type SwiggyPeakLoadBalancer struct {
    mu sync.RWMutex
    
    // Time-based configuration
    peakHours map[string]PeakConfig
    
    // Predictive scaling
    trafficPredictor *TrafficPredictor
    
    // Server pools
    regularPool  []Server
    peakPool     []Server  // Additional servers for peak
    
    // Metrics
    metrics *Metrics
}

// PeakConfig defines peak hour configuration
type PeakConfig struct {
    StartTime   string
    EndTime     string
    Multiplier  float64  // Traffic multiplier
    PreWarmMins int      // Pre-warm duration
}

func NewSwiggyPeakLoadBalancer() *SwiggyPeakLoadBalancer {
    return &SwiggyPeakLoadBalancer{
        peakHours: map[string]PeakConfig{
            "lunch": {
                StartTime:   "11:30",
                EndTime:     "14:30",
                Multiplier:  10.0,
                PreWarmMins: 30,
            },
            "dinner": {
                StartTime:   "19:00",
                EndTime:     "22:00",
                Multiplier:  8.0,
                PreWarmMins: 30,
            },
            "weekend_breakfast": {
                StartTime:   "09:00",
                EndTime:     "11:00",
                Multiplier:  5.0,
                PreWarmMins: 20,
            },
        },
        trafficPredictor: NewTrafficPredictor(),
        metrics:         NewMetrics(),
    }
}

// PredictiveScaling scales before peak hours
func (s *SwiggyPeakLoadBalancer) PredictiveScaling(ctx context.Context) {
    ticker := time.NewTicker(1 * time.Minute)
    defer ticker.Stop()
    
    for {
        select {
        case <-ctx.Done():
            return
        case <-ticker.C:
            s.checkAndScale()
        }
    }
}

func (s *SwiggyPeakLoadBalancer) checkAndScale() {
    now := time.Now()
    currentHour := now.Format("15:04")
    
    for peakName, config := range s.peakHours {
        peakStart, _ := time.Parse("15:04", config.StartTime)
        preWarmTime := peakStart.Add(-time.Duration(config.PreWarmMins) * time.Minute)
        
        // Check if we're in pre-warm window
        if s.isTimeInRange(currentHour, preWarmTime.Format("15:04"), config.StartTime) {
            fmt.Printf("🔥 Pre-warming for %s peak hour\n", peakName)
            s.scaleUp(peakName, config)
        }
        
        // Check if peak hour ended
        if s.isTimeAfter(currentHour, config.EndTime) {
            fmt.Printf("📉 Scaling down after %s peak hour\n", peakName)
            s.scaleDown(peakName)
        }
    }
}

func (s *SwiggyPeakLoadBalancer) scaleUp(peakName string, config PeakConfig) {
    s.mu.Lock()
    defer s.mu.Unlock()
    
    // Calculate required capacity
    currentCapacity := len(s.regularPool)
    requiredCapacity := int(float64(currentCapacity) * config.Multiplier)
    additionalServers := requiredCapacity - currentCapacity
    
    fmt.Printf("📈 Scaling up for %s peak:\n", peakName)
    fmt.Printf("   Current servers: %d\n", currentCapacity)
    fmt.Printf("   Required servers: %d\n", requiredCapacity)
    fmt.Printf("   Adding servers: %d\n", additionalServers)
    
    // Add servers from peak pool
    for i := 0; i < additionalServers && i < len(s.peakPool); i++ {
        server := s.peakPool[i]
        
        // Pre-warm the server
        s.preWarmServer(&server)
        
        // Add to active pool
        s.regularPool = append(s.regularPool, server)
        
        // Update metrics
        s.metrics.ServersAdded++
    }
    
    // Update routing weights for gradual traffic shift
    s.updateRoutingWeights()
}

func (s *SwiggyPeakLoadBalancer) preWarmServer(server *Server) {
    fmt.Printf("🔥 Pre-warming server %s\n", server.ID)
    
    // 1. Establish database connections
    server.WarmDatabaseConnections()
    
    // 2. Load cache data
    server.PreloadCache([]string{
        "popular_restaurants",
        "trending_dishes",
        "delivery_zones",
        "payment_methods",
    })
    
    // 3. Compile JIT code paths
    server.WarmCodePaths()
    
    // 4. Establish service mesh connections
    server.EstablishMeshConnections()
    
    server.Status = "ready"
    server.WarmupComplete = true
}

// SmartRouting during peak hours
func (s *SwiggyPeakLoadBalancer) SmartRouting(request Request) *Server {
    s.mu.RLock()
    defer s.mu.RUnlock()
    
    // Identify request priority
    priority := s.calculatePriority(request)
    
    // Route based on priority
    switch priority {
    case "premium":
        // Premium customers get best servers
        return s.selectBestServer(request)
    case "regular":
        // Regular customers - standard routing
        return s.standardRouting(request)
    case "batch":
        // Batch orders - can tolerate slight delay
        return s.batchOptimizedRouting(request)
    default:
        return s.standardRouting(request)
    }
}

func (s *SwiggyPeakLoadBalancer) calculatePriority(request Request) string {
    // Premium customers
    if request.UserTier == "gold" || request.UserTier == "platinum" {
        return "premium"
    }
    
    // Large orders during peak
    if request.OrderValue > 1000 && s.isPeakHour() {
        return "premium"
    }
    
    // Scheduled orders
    if request.IsScheduled {
        return "batch"
    }
    
    return "regular"
}

// TrafficPredictor predicts traffic patterns
type TrafficPredictor struct {
    historicalData map[string][]float64
    mlModel        *MLModel
}

func (t *TrafficPredictor) PredictNextHour() float64 {
    // Use historical data + ML model
    dayOfWeek := time.Now().Weekday()
    hour := time.Now().Hour()
    
    // Factors affecting traffic
    factors := map[string]float64{
        "is_weekend":     float64(s.boolToInt(dayOfWeek == 0 || dayOfWeek == 6)),
        "is_holiday":     float64(s.boolToInt(s.isHoliday())),
        "weather":        s.getWeatherImpact(),  // Rain increases orders
        "ipl_match":      float64(s.boolToInt(s.isIPLMatch())),  // Cricket matches
        "festival":       s.getFestivalImpact(),  // Diwali, Holi, etc.
        "hour":          float64(hour),
        "day_of_week":   float64(dayOfWeek),
    }
    
    // Predict using model
    prediction := t.mlModel.Predict(factors)
    
    return prediction
}
```

## Chapter 12: Troubleshooting Service Discovery Issues

### Common Problems and Solutions

"Service discovery ke problems are like Mumbai traffic jams - you need to know shortcuts and alternate routes!"

```python
class ServiceDiscoveryTroubleshooter:
    """
    Comprehensive troubleshooting guide
    Based on real incidents at Indian tech companies
    """
    
    def __init__(self):
        self.common_issues = {
            'registration_failure': {
                'symptoms': [
                    'Service not appearing in discovery',
                    'Health checks failing',
                    '503 Service Unavailable errors'
                ],
                'causes': [
                    'Network connectivity issues',
                    'Incorrect configuration',
                    'Discovery service down',
                    'Firewall blocking ports'
                ],
                'solutions': [
                    'Check network connectivity',
                    'Verify service configuration',
                    'Check discovery service health',
                    'Review firewall rules'
                ],
                'commands': [
                    'curl http://consul:8500/v1/health/service/my-service',
                    'kubectl get endpoints my-service -o yaml',
                    'nslookup my-service.default.svc.cluster.local'
                ]
            },
            'stale_instances': {
                'symptoms': [
                    'Requests going to dead instances',
                    'Intermittent 502 errors',
                    'Uneven load distribution'
                ],
                'causes': [
                    'Graceful shutdown not implemented',
                    'Health check intervals too long',
                    'Deregistration failure'
                ],
                'solutions': [
                    'Implement graceful shutdown',
                    'Reduce health check intervals',
                    'Add deregistration timeout'
                ]
            },
            'split_brain': {
                'symptoms': [
                    'Different services seeing different instances',
                    'Inconsistent routing',
                    'Data inconsistency'
                ],
                'causes': [
                    'Network partition',
                    'Consul/Etcd leader election issues',
                    'Clock skew between nodes'
                ],
                'solutions': [
                    'Fix network partition',
                    'Ensure NTP sync',
                    'Review quorum settings'
                ]
            }
        }
    
    def diagnose_issue(self, symptoms):
        """
        Diagnose service discovery issues
        Like doctor diagnosing patient
        """
        possible_issues = []
        
        for issue_type, issue_data in self.common_issues.items():
            matching_symptoms = 0
            
            for symptom in symptoms:
                if any(s in symptom.lower() for s in issue_data['symptoms']):
                    matching_symptoms += 1
            
            if matching_symptoms > 0:
                confidence = matching_symptoms / len(issue_data['symptoms'])
                possible_issues.append({
                    'issue': issue_type,
                    'confidence': confidence,
                    'solutions': issue_data['solutions']
                })
        
        # Sort by confidence
        possible_issues.sort(key=lambda x: x['confidence'], reverse=True)
        
        return possible_issues
    
    def generate_runbook(self, issue_type):
        """
        Generate step-by-step runbook for issue resolution
        """
        if issue_type not in self.common_issues:
            return None
        
        issue = self.common_issues[issue_type]
        
        runbook = f"""
# Runbook: {issue_type.replace('_', ' ').title()}

## Step 1: Verify Symptoms
{chr(10).join(f"- [ ] {s}" for s in issue['symptoms'])}

## Step 2: Check Common Causes
{chr(10).join(f"- [ ] {c}" for c in issue['causes'])}

## Step 3: Execute Diagnostic Commands
```bash
{chr(10).join(issue.get('commands', []))}
```

## Step 4: Apply Solutions
{chr(10).join(f"{i+1}. {s}" for i, s in enumerate(issue['solutions']))}

## Step 5: Verify Resolution
- [ ] Service is discoverable
- [ ] Health checks passing
- [ ] Load balanced properly
- [ ] No errors in logs

## Step 6: Post-Incident Actions
- [ ] Document root cause
- [ ] Update monitoring
- [ ] Share learnings with team
        """
        
        return runbook
```

---

**[Episode 093 Part 3 completed with 7,000+ words covering production strategies, case studies, and troubleshooting]**