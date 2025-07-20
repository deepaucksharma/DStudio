---
title: Load Balancing Pattern
description: Pattern for distributed systems coordination and reliability
type: pattern
difficulty: intermediate
reading_time: 20 min
prerequisites: []
pattern_type: "general"
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](../index.md) → [Part III: Patterns](index.md) → **Load Balancing Pattern**

# Load Balancing Pattern

**Distributing work across multiple resources**

> *"Many hands make light work—if coordinated properly."*

---

## 🎯 Level 1: Intuition

### The Checkout Line Analogy

Load balancing is like grocery store checkout:
- **Multiple lines**: Several cashiers available
- **Shortest line**: Join the line with fewest people
- **Express lane**: Special line for small baskets
- **Closed register**: Avoid lines that aren't operating

### Basic Load Balancer

```python
import random
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Server:
    id: str
    address: str
    healthy: bool = True
    current_connections: int = 0

class SimpleLoadBalancer:
    def __init__(self, servers: List[Server]):
        self.servers = servers
        self.current_index = 0

    def get_server_round_robin(self) -> Optional[Server]:
        """Round-robin load balancing"""
        if not self.servers:
            return None

        # Find next healthy server
        attempts = len(self.servers)
        while attempts > 0:
            server = self.servers[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.servers)

            if server.healthy:
                return server

            attempts -= 1

        return None  # No healthy servers

    def get_server_random(self) -> Optional[Server]:
        """Random load balancing"""
        healthy_servers = [s for s in self.servers if s.healthy]
        if not healthy_servers:
            return None

        return random.choice(healthy_servers)

    def get_server_least_connections(self) -> Optional[Server]:
        """Least connections load balancing"""
        healthy_servers = [s for s in self.servers if s.healthy]
        if not healthy_servers:
            return None

        return min(healthy_servers, key=lambda s: s.current_connections)
```

---

## 🏗️ Level 2: Foundation

### Load Balancing Algorithms

| Algorithm | Description | Pros | Cons |
|-----------|-------------|------|------|
| **Round Robin** | Sequential distribution | Simple, fair | Ignores server load |
| **Weighted Round Robin** | Proportional to capacity | Handles different server sizes | Static weights |
| **Least Connections** | Route to least busy | Dynamic load awareness | Connection tracking overhead |
| **Least Response Time** | Route to fastest | Performance optimized | Requires latency monitoring |
| **IP Hash** | Consistent routing | Session affinity | Uneven distribution possible |
| **Random** | Random selection | Simple, no state | No optimization |

### Implementing Advanced Algorithms

```python
import time
import hashlib
from collections import defaultdict
from typing import Dict, Tuple

class AdvancedLoadBalancer:
    def __init__(self):
        self.servers = []
        self.weights = {}  # Server weights for WRR
        self.response_times = defaultdict(list)  # Track response times
        self.connections = defaultdict(int)  # Active connections

    def add_server(self, server: Server, weight: int = 1):
        """Add server with weight"""
        self.servers.append(server)
        self.weights[server.id] = weight

    def weighted_round_robin(self) -> Optional[Server]:
        """Weighted round-robin implementation"""
        if not self.servers:
            return None

        # Build weighted list
        weighted_servers = []
        for server in self.servers:
            if server.healthy:
                weight = self.weights.get(server.id, 1)
                weighted_servers.extend([server] * weight)

        if not weighted_servers:
            return None

        # Use class variable to track position
        if not hasattr(self, '_wrr_index'):
            self._wrr_index = 0

        server = weighted_servers[self._wrr_index % len(weighted_servers)]
        self._wrr_index += 1

        return server

    def least_response_time(self) -> Optional[Server]:
        """Route to server with lowest average response time"""
        healthy_servers = [s for s in self.servers if s.healthy]
        if not healthy_servers:
            return None

        # Calculate average response times
        server_scores = []
        for server in healthy_servers:
            if server.id in self.response_times:
                avg_time = sum(self.response_times[server.id][-10:]) / len(self.response_times[server.id][-10:])
            else:
                avg_time = 0  # No data, optimistic

            # Factor in current connections
            connection_penalty = self.connections[server.id] * 0.1
            score = avg_time + connection_penalty

            server_scores.append((server, score))

        # Return server with lowest score
        return min(server_scores, key=lambda x: x[1])[0]

    def consistent_hash(self, key: str) -> Optional[Server]:
        """Consistent hashing for session affinity"""
        if not self.servers:
            return None

        healthy_servers = [s for s in self.servers if s.healthy]
        if not healthy_servers:
            return None

        # Hash the key
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)

        # Simple modulo (not true consistent hashing, see Level 3)
        index = hash_value % len(healthy_servers)
        return healthy_servers[index]

    def power_of_two_choices(self) -> Optional[Server]:
        """Randomly pick two servers, choose the less loaded one"""
        healthy_servers = [s for s in self.servers if s.healthy]
        if not healthy_servers:
            return None

        if len(healthy_servers) == 1:
            return healthy_servers[0]

        # Pick two random servers
        choices = random.sample(healthy_servers, min(2, len(healthy_servers)))

        # Return the one with fewer connections
        return min(choices, key=lambda s: self.connections[s.id])
```

---

## 🔧 Level 3: Deep Dive

### Layer 4 vs Layer 7 Load Balancing

```python
class Layer4LoadBalancer:
    """
    Transport layer (TCP/UDP) load balancing
    - Faster, less CPU intensive
    - No application awareness
    - Can't route based on content
    """

    def handle_connection(self, client_socket):
        # Select backend server
        server = self.select_server()
        if not server:
            client_socket.close()
            return

        # Create connection to backend
        backend_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend_socket.connect((server.address, server.port))

        # Bi-directional proxy
        self.proxy_data(client_socket, backend_socket)

class Layer7LoadBalancer:
    """
    Application layer (HTTP) load balancing
    - Content-aware routing
    - Can modify requests/responses
    - Higher CPU usage
    """

    def handle_http_request(self, request):
        # Parse HTTP request
        parsed = self.parse_http_request(request)

        # Content-based routing
        if parsed.path.startswith('/api/'):
            server = self.select_api_server()
        elif parsed.path.startswith('/static/'):
            server = self.select_static_server()
        else:
            server = self.select_web_server()

        # Can modify headers
        request.headers['X-Forwarded-For'] = request.client_ip
        request.headers['X-Real-IP'] = request.client_ip

        # Forward to selected server
        response = self.forward_request(server, request)

        # Can modify response
        response.headers['X-Served-By'] = server.id

        return response
```

### Consistent Hashing Implementation

```python
import bisect
import hashlib

class ConsistentHashLoadBalancer:
    """
    True consistent hashing with virtual nodes
    """

    def __init__(self, virtual_nodes: int = 150):
        self.servers = {}
        self.ring = {}  # hash -> server
        self.sorted_keys = []
        self.virtual_nodes = virtual_nodes

    def _hash(self, key: str) -> int:
        """Generate hash value"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_server(self, server: Server):
        """Add server to the ring"""
        self.servers[server.id] = server

        # Add virtual nodes
        for i in range(self.virtual_nodes):
            virtual_key = f"{server.id}:{i}"
            hash_value = self._hash(virtual_key)
            self.ring[hash_value] = server
            bisect.insort(self.sorted_keys, hash_value)

    def remove_server(self, server_id: str):
        """Remove server from the ring"""
        if server_id not in self.servers:
            return

        # Remove virtual nodes
        for i in range(self.virtual_nodes):
            virtual_key = f"{server_id}:{i}"
            hash_value = self._hash(virtual_key)

            if hash_value in self.ring:
                del self.ring[hash_value]
                self.sorted_keys.remove(hash_value)

        del self.servers[server_id]

    def get_server(self, key: str) -> Optional[Server]:
        """Get server for a given key"""
        if not self.ring:
            return None

        hash_value = self._hash(key)

        # Find the first server clockwise from the hash
        index = bisect.bisect_right(self.sorted_keys, hash_value)

        # Wrap around if necessary
        if index == len(self.sorted_keys):
            index = 0

        server_hash = self.sorted_keys[index]
        return self.ring[server_hash]

    def get_n_servers(self, key: str, n: int) -> List[Server]:
        """Get n servers for replication"""
        if not self.ring or n <= 0:
            return []

        servers = []
        seen = set()

        hash_value = self._hash(key)
        index = bisect.bisect_right(self.sorted_keys, hash_value)

        while len(servers) < n and len(seen) < len(self.servers):
            if index >= len(self.sorted_keys):
                index = 0

            server_hash = self.sorted_keys[index]
            server = self.ring[server_hash]

            if server.id not in seen:
                servers.append(server)
                seen.add(server.id)

            index += 1

        return servers
```

### Geographic Load Balancing

```python
import geoip2.database
from math import radians, sin, cos, sqrt, atan2

class GeographicLoadBalancer:
    """
    Route requests to nearest datacenter
    """

    def __init__(self, geoip_db_path: str):
        self.reader = geoip2.database.Reader(geoip_db_path)
        self.datacenters = []

    def add_datacenter(self, name: str, latitude: float, longitude: float, servers: List[Server]):
        """Add datacenter with location"""
        self.datacenters.append({
            'name': name,
            'lat': latitude,
            'lon': longitude,
            'servers': servers
        })

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points (in km)"""
        R = 6371  # Earth radius in km

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        return R * c

    def get_nearest_datacenter(self, client_ip: str) -> Optional[dict]:
        """Find nearest datacenter for client"""
        try:
            response = self.reader.city(client_ip)
            client_lat = response.location.latitude
            client_lon = response.location.longitude
        except:
            # Default to first datacenter if geo lookup fails
            return self.datacenters[0] if self.datacenters else None

        nearest = None
        min_distance = float('inf')

        for dc in self.datacenters:
            distance = self.calculate_distance(
                client_lat, client_lon,
                dc['lat'], dc['lon']
            )

            if distance < min_distance:
                min_distance = distance
                nearest = dc

        return nearest

    def route_request(self, client_ip: str) -> Optional[Server]:
        """Route to server in nearest datacenter"""
        datacenter = self.get_nearest_datacenter(client_ip)
        if not datacenter:
            return None

        # Use least connections within the datacenter
        healthy_servers = [s for s in datacenter['servers'] if s.healthy]
        if not healthy_servers:
            # Try next nearest datacenter
            return self.fallback_routing(client_ip)

        return min(healthy_servers, key=lambda s: s.current_connections)
```

---

## 🚀 Level 4: Expert

### Production Load Balancing Systems

#### HAProxy Configuration Patterns
{% raw %}
```python
class HAProxyConfig:
    """
    Generate HAProxy configurations for different scenarios
    """

    def generate_http_config(self,
                           backends: List[dict],
                           algorithm: str = "leastconn") -> str:
        """Generate HTTP load balancing config"""
        config = """
global
    maxconn 100000
    log stdout local0

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms
    option httplog

frontend web_frontend
    bind *:80
    bind *:443 ssl crt /etc/ssl/cert.pem

    # Rate limiting
    stick-table type ip size 100k expire 30s store http_req_rate(10s)
    http-request track-sc0 src
    http-request deny if { sc_http_req_rate(0) gt 100 }

    # Route based on host header
    acl is_api hdr(host) -i api.example.com
    acl is_static path_beg /static /images /css /js

    use_backend api_backend if is_api
    use_backend static_backend if is_static
    default_backend web_backend

backend web_backend
    balance {algorithm}
    option httpchk GET /health

    # Enable sticky sessions
    cookie SERVERID insert indirect nocache
"""

        # Add servers
        for i, backend in enumerate(backends):
            config += f"""
    server web{{i}} {{backend['address']}}:{{backend['port']}} \\
        check inter 2000 rise 2 fall 3 \\
        cookie web{{i}} \\
        maxconn {{backend.get('max_conn', 1000)}}
"""

        return config

    def generate_tcp_config(self, service: str, backends: List[dict]) -> str:
        """Generate TCP (Layer 4) load balancing config"""
        if service == 'mysql':
            return self._mysql_config(backends)
        elif service == 'redis':
            return self._redis_config(backends)
        else:
            return self._generic_tcp_config(backends)

    def _mysql_config(self, backends: List[dict]) -> str:
        """MySQL-specific load balancing"""
        config = """
listen mysql_cluster
    bind *:3306
    mode tcp
    balance leastconn
    option mysql-check user haproxy_check

    # Read/write split
"""

        for i, backend in enumerate(backends):
            if backend.get('role') == 'master':
                config += f"""
    server mysql_master_{{i}} {{backend['address']}}:3306 check
"""
            else:
                config += f"""
    server mysql_slave_{{i}} {{backend['address']}}:3306 check backup
"""

        return config
```
{% endraw %}

#### NGINX Advanced Load Balancing
{% raw %}
```python
class NginxLoadBalancer:
    """
    NGINX Plus advanced load balancing features
    """

    def generate_upstream_config(self,
                                name: str,
                                servers: List[dict],
                                method: str = "least_conn") -> str:
        """Generate upstream configuration"""
        config = f"""
upstream {name} {{
    {method};

    # Enable keepalive connections
    keepalive 32;

    # Health checking (NGINX Plus)
    zone {name}_zone 64k;
"""

        for server in servers:
            options = []

            if server.get('weight'):
                options.append(f"weight={server['weight']}")

            if server.get('max_fails'):
                options.append(f"max_fails={server['max_fails']}")

            if server.get('fail_timeout'):
                options.append(f"fail_timeout={server['fail_timeout']}")

            if server.get('backup'):
                options.append("backup")

            if server.get('down'):
                options.append("down")

            options_str = " ".join(options)
            config += f"""
    server {{server['address']}}:{{server['port']}} {{options_str}};
"""

        config += """
}
"""
        return config

    def generate_location_config(self,
                               location: str,
                               upstream: str,
                               cache: bool = False) -> str:
        """Generate location block with load balancing"""
        config = f"""
location {{location}} {{{{
    proxy_pass http://{{upstream}};

    # Add headers
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # Connection settings
    proxy_http_version 1.1;
    proxy_set_header Connection "";
"""

        if cache:
            config += """
    # Caching
    proxy_cache my_cache;
    proxy_cache_key "$scheme$request_method$host$request_uri";
    proxy_cache_valid 200 302 10m;
    proxy_cache_valid 404 1m;
    proxy_cache_bypass $http_pragma $http_authorization;
"""

        config += """
    # Timeouts
    proxy_connect_timeout 5s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    # Buffering
    proxy_buffering on;
    proxy_buffer_size 4k;
    proxy_buffers 8 4k;
}
"""
        return config
```
{% endraw %}

### Real-World Case Study: Netflix's Zuul

```python
class ZuulLoadBalancer:
    """
    Netflix Zuul's approach to load balancing
    """

    def __init__(self):
        self.discovery_client = EurekaClient()
        self.stats = ServerStats()
        self.rule = WeightedResponseTimeRule()

    def choose_server(self,
                     service_name: str,
                     request_context: dict) -> Optional[Server]:
        """
        Choose server using Netflix's approach
        """
        # Get available servers from Eureka
        servers = self.discovery_client.get_instances(service_name)

        if not servers:
            return None

        # Filter based on zone affinity
        zone = request_context.get('zone')
        if zone:
            zone_servers = [s for s in servers if s.zone == zone]
            if zone_servers:
                servers = zone_servers

        # Apply circuit breaker status
        available_servers = []
        for server in servers:
            circuit_breaker = self.get_circuit_breaker(server)
            if not circuit_breaker.is_open():
                available_servers.append(server)

        if not available_servers:
            # All circuits open, try anyway
            available_servers = servers

        # Use rule to select
        return self.rule.choose(available_servers, request_context)

class WeightedResponseTimeRule:
    """
    Netflix's weighted response time rule
    """

    def __init__(self):
        self.response_times = defaultdict(lambda: deque(maxlen=100))
        self.last_update = defaultdict(float)

    def choose(self, servers: List[Server], context: dict) -> Server:
        """Choose server based on response times"""
        if len(servers) == 1:
            return servers[0]

        # Calculate weights based on response time
        weights = []
        total_response_time = 0

        for server in servers:
            avg_time = self.get_average_response_time(server)
            total_response_time += avg_time
            weights.append(avg_time)

        # Invert weights (lower response time = higher weight)
        if total_response_time > 0:
            weights = [total_response_time - w for w in weights]
        else:
            # No data, use equal weights
            weights = [1] * len(servers)

        # Weighted random selection
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(servers)

        r = random.uniform(0, total_weight)

        for i, weight in enumerate(weights):
            r -= weight
            if r <= 0:
                return servers[i]

        return servers[-1]

    def record_response_time(self, server: Server, response_time: float):
        """Record response time for a server"""
        self.response_times[server.id].append(response_time)
        self.last_update[server.id] = time.time()

    def get_average_response_time(self, server: Server) -> float:
        """Get average response time for server"""
        times = self.response_times[server.id]
        if not times:
            return 1.0  # Default

        # Exponential decay for old measurements
        now = time.time()
        last_update = self.last_update[server.id]
        age_seconds = now - last_update

        avg = sum(times) / len(times)

        # Increase weight for stale data
        if age_seconds > 60:
            avg *= (1 + age_seconds / 60)

        return avg
```

---

## 🎯 Level 5: Mastery

### Theoretical Optimal Load Balancing

```python
import numpy as np
from scipy.optimize import linear_sum_assignment

class OptimalLoadBalancer:
    """
    Mathematically optimal load balancing
    """

    def __init__(self):
        self.servers = []
        self.requests = []

    def calculate_cost_matrix(self,
                            requests: List[dict],
                            servers: List[Server]) -> np.ndarray:
        """
        Calculate cost of assigning each request to each server
        """
        n_requests = len(requests)
        n_servers = len(servers)

        # Cost matrix
        costs = np.zeros((n_requests, n_servers))

        for i, request in enumerate(requests):
            for j, server in enumerate(servers):
                # Latency cost
                latency = self.estimate_latency(request, server)

                # Load cost (quadratic to penalize imbalance)
                current_load = server.current_connections
                load_cost = (current_load + 1) ** 2

                # Resource cost
                resource_cost = self.calculate_resource_cost(request, server)

                # Combined cost
                costs[i][j] = (
                    0.5 * latency +
                    0.3 * load_cost +
                    0.2 * resource_cost
                )

                # Infinite cost if server can't handle request
                if not self.can_handle(request, server):
                    costs[i][j] = np.inf

        return costs

    def optimal_assignment(self,
                         requests: List[dict],
                         servers: List[Server]) -> dict:
        """
        Find optimal request-to-server assignment
        """
        if not requests or not servers:
            return {}

        # Calculate cost matrix
        costs = self.calculate_cost_matrix(requests, servers)

        # Handle case where requests > servers
        if len(requests) > len(servers):
            # Replicate servers
            n_copies = (len(requests) + len(servers) - 1) // len(servers)
            expanded_costs = np.tile(costs[:, :], (1, n_copies))
            costs = expanded_costs[:, :len(requests)]

        # Solve assignment problem
        row_indices, col_indices = linear_sum_assignment(costs)

        # Build assignment map
        assignments = {}
        for i, j in zip(row_indices, col_indices):
            server_idx = j % len(servers)
            assignments[requests[i]['id']] = servers[server_idx]

        return assignments

    def power_law_aware_balancing(self,
                                 request_sizes: List[float]) -> dict:
        """
        Handle power-law distributed request sizes
        (Few very large requests, many small ones)
        """
        # Sort requests by size
        indexed_sizes = [(i, size) for i, size in enumerate(request_sizes)]
        indexed_sizes.sort(key=lambda x: x[1], reverse=True)

        # Assign large requests first to ensure they get resources
        assignments = {}
        server_loads = [0] * len(self.servers)

        for idx, size in indexed_sizes:
            # Find server with capacity for this request
            best_server = None
            best_score = float('inf')

            for i, server in enumerate(self.servers):
                if server_loads[i] + size <= server.capacity:
                    # Score based on resulting balance
                    new_load = server_loads[i] + size
                    imbalance = np.std(server_loads)
                    score = new_load + 10 * imbalance

                    if score < best_score:
                        best_score = score
                        best_server = i

            if best_server is not None:
                assignments[idx] = self.servers[best_server]
                server_loads[best_server] += size
            else:
                # No server has capacity - need to reject or queue
                assignments[idx] = None

        return assignments
```

### Future Directions

1. **ML-Driven Load Balancing**: Predict optimal routing using deep learning
2. **Quantum Load Balancing**: Superposition of routing states
3. **Blockchain Load Balancing**: Decentralized consensus on routing
4. **Biological-Inspired**: Ant colony optimization for dynamic routing

---

## 📋 Quick Reference

### Load Balancing Algorithm Selection

| Scenario | Best Algorithm | Why |
|----------|---------------|-----|
| Stateless API | Least Connections | Actual load awareness |
| Session-based | IP Hash | Session persistence |
| Varied server capacity | Weighted Round Robin | Proportional distribution |
| Global service | Geographic | Minimize latency |
| Microservices | Service Mesh | Advanced routing rules |

### Implementation Checklist

- [ ] Choose appropriate algorithm
- [ ] Implement health checking
- [ ] Configure connection draining
- [ ] Add monitoring metrics
- [ ] Test failover scenarios
- [ ] Document server weights
- [ ] Plan for maintenance mode
- [ ] Monitor distribution fairness

---

---

*"Perfect balance is not the goal—effective distribution is."*

---

**Previous**: [← Leader Election Pattern](leader-election.md) | **Next**: [Load Shedding Pattern →](load-shedding.md)
